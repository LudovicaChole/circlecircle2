"""Offline, signed IPv4-bound licenses. This module holds no signing secret."""
import base64
import ipaddress
import json
import os
import tempfile
import hashlib
import hmac
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

from utilities.error_messages import error_message
from utilities.device_info import local_ipv4_addresses
from utilities.app_paths import config_directory, resource_directory

PUBLIC_KEY_PATH = config_directory() / 'public_key.pem'


def ensure_public_key():
    """Copy an existing verification key to writable config without rotating it."""
    PUBLIC_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PUBLIC_KEY_PATH.exists():
        for source in (resource_directory() / 'utilities' / 'license_public_key.pem',
                       resource_directory() / 'config' / 'public_key.pem'):
            if source.is_file() and source != PUBLIC_KEY_PATH:
                atomic_write(PUBLIC_KEY_PATH, source.read_text(encoding='ascii'))
                break
    return PUBLIC_KEY_PATH
_TEMPORARY_CODE_HASH = '361493207a61036657b79ebc427fbb679fb28f5d2181e539f327ad9fcde640f7'


def temporary_signature(encoded):
    return hmac.new(bytes.fromhex(_TEMPORARY_CODE_HASH),
                    b'CircleCircle2.C2T1.' + encoded.encode('ascii'), hashlib.sha256).hexdigest()


def license_path():
    return config_directory() / 'circlecircle2.lic'


def legacy_license_path():
    base = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share'))
    return base / 'CircleCircle2' / 'license.json'


def encode_bytes(value):
    return base64.urlsafe_b64encode(value).decode('ascii').rstrip('=')


def decode_bytes(value):
    return base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)


def atomic_write(path, text, *, encoding='utf-8', newline=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding=encoding, newline=newline) as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass(frozen=True)
class LicenseStatus:
    valid: bool
    message: str
    ipv4: str = ''
    expires_at: str = ''


class LicenseManager:
    def __init__(self, path=None, public_key_path=None, address_provider=None, clock=None):
        self.path = Path(path) if path is not None else license_path()
        self.legacy_path = legacy_license_path() if path is None else None
        self.public_key_path = Path(public_key_path) if public_key_path is not None else ensure_public_key()
        self.address_provider = address_provider or local_ipv4_addresses
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def validate(self, token):
        ipv4 = expires_at = ''
        try:
            compact = ''.join(token.split())
            if compact.startswith('C2T1.'):
                return self.validate_temporary(compact)
            from cryptography.hazmat.primitives.serialization import load_pem_public_key
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            compact = ''.join(token.split())
            if len(compact) > 8192:
                raise ValueError('Activation code is too long.')
            prefix, encoded, signature = compact.split('.')
            if prefix != 'C2V1':
                raise ValueError('Unsupported activation code.')
            key = load_pem_public_key(self.public_key_path.read_bytes())
            if not isinstance(key, Ed25519PublicKey):
                raise ValueError('Invalid license verification key.')
            payload = decode_bytes(encoded)
            key.verify(decode_bytes(signature), b'C2V1.' + encoded.encode('ascii'))
            data = json.loads(payload)
            if data['product'] != 'CircleCircle2' or data['version'] != 1:
                raise ValueError('This code is for another product.')
            ipv4 = str(ipaddress.IPv4Address(data['ipv4']))
            issued = datetime.fromisoformat(data['issued_at'])
            expires = datetime.fromisoformat(data['expires_at'])
            expires_at = expires.astimezone().isoformat(timespec='seconds')
            now = self.clock()
            if issued.tzinfo is None or expires.tzinfo is None or expires <= issued:
                raise ValueError('Invalid license validity period.')
            if now < issued:
                raise ValueError('License is not valid yet; check the system date.')
            if now >= expires:
                raise ValueError('License has expired.')
            if ipv4 not in self.address_provider():
                raise ValueError(f'License IPv4 {ipv4} does not match this computer.')
            return LicenseStatus(True, 'License is valid.', ipv4, expires_at)
        except FileNotFoundError:
            message = 'License verification key is missing. Restore the application files or contact the administrator.'
        except ImportError:
            message = 'The cryptography package is required to verify licenses.'
        except Exception as error:
            message = error_message(error) or 'Invalid activation code or signature.'
        return LicenseStatus(False, message, ipv4, expires_at)

    def validate_temporary(self, token):
        try:
            if len(token) > 8192:
                raise ValueError('Invalid temporary activation.')
            prefix, encoded, signature = token.split('.')
            if prefix != 'C2T1' or not hmac.compare_digest(signature, temporary_signature(encoded)):
                raise ValueError('Invalid temporary activation.')
            data = json.loads(decode_bytes(encoded))
            issued = datetime.fromisoformat(data['issued_at'])
            expires = datetime.fromisoformat(data['expires_at'])
            if (data['product'] != 'CircleCircle2' or issued.tzinfo is None or expires.tzinfo is None
                    or expires - issued != timedelta(days=1)):
                raise ValueError('Invalid temporary activation period.')
            expiration = expires.astimezone().isoformat(timespec='seconds')
            now = self.clock()
            if now < issued:
                return LicenseStatus(False, 'Check the system date; temporary activation is not valid yet.', expires_at=expiration)
            if now >= expires:
                return LicenseStatus(False, 'Temporary 1-day access has expired.', expires_at=expiration)
            return LicenseStatus(True, 'Temporary access is available for 1 day (24 hours) from activation.', expires_at=expiration)
        except Exception as error:
            return LicenseStatus(False, error_message(error) or 'Invalid temporary activation.')

    def status(self):
        if not self.path.exists():
            if self.legacy_path and self.legacy_path.is_file():
                try:
                    record = json.loads(self.legacy_path.read_text(encoding='utf-8'))
                    return self.activate(record['token'])
                except (OSError, ValueError, KeyError, TypeError) as error:
                    return LicenseStatus(False, f'Cannot migrate saved license: {error_message(error)}')
            return LicenseStatus(False, 'Software has not been activated.')
        try:
            text = self.path.read_text(encoding='utf-8').strip()
            token = json.loads(text)['token'] if text.startswith('{') else text
            return self.validate(token)
        except (OSError, ValueError, KeyError, TypeError) as error:
            return LicenseStatus(False, f'Cannot read saved license: {error_message(error)}')

    def activate(self, token):
        compact = ''.join(token.split())
        if hmac.compare_digest(hashlib.sha256(compact.encode('utf-8')).hexdigest(), _TEMPORARY_CODE_HASH):
            now = self.clock()
            if now.tzinfo is None:
                return LicenseStatus(False, 'The activation time must include a time zone.')
            encoded = encode_bytes(json.dumps({'product': 'CircleCircle2',
                'issued_at': now.isoformat(), 'expires_at': (now + timedelta(days=1)).isoformat()},
                sort_keys=True, separators=(',', ':')).encode('utf-8'))
            compact = 'C2T1.' + encoded + '.' + temporary_signature(encoded)
            status = self.validate(compact)
            if status.valid:
                atomic_write(self.path, compact + '\n')
            return status
        status = self.validate(token)
        if status.valid:
            atomic_write(self.path, ''.join(token.split()) + '\n')
        return status
