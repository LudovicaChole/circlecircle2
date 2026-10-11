import sys
from pathlib import Path
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Administrator-only license issuer; do not ship its private key with the app."""
import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

from utilities.licensing import PUBLIC_KEY_PATH, atomic_write, encode_bytes, ensure_public_key
from utilities.app_paths import config_directory

PRIVATE_KEY_PATH = config_directory() / 'private_key.pem'


def signing_key(private_path=PRIVATE_KEY_PATH, public_path=PUBLIC_KEY_PATH):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    private_path, public_path = Path(private_path), Path(public_path)
    if private_path == PRIVATE_KEY_PATH and public_path == PUBLIC_KEY_PATH:
        ensure_public_key()
        old_private = config_directory() / 'license_issuer' / 'private_key.pem'
        if not private_path.exists() and old_private.is_file():
            atomic_write(private_path, old_private.read_text(encoding='ascii'))
    if private_path.exists():
        key = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError('Unsupported signing key.')
    else:
        if public_path.exists():
            raise ValueError('The issuer private key is missing. Restore it; do not replace the public key.')
        key = Ed25519PrivateKey.generate()
        private_path.parent.mkdir(parents=True, exist_ok=True)
        with private_path.open('xb') as stream:
            stream.write(key.private_bytes(serialization.Encoding.PEM,
                                          serialization.PrivateFormat.PKCS8,
                                          serialization.NoEncryption()))
    public = key.public_key().public_bytes(serialization.Encoding.PEM,
                                          serialization.PublicFormat.SubjectPublicKeyInfo)
    if public_path.exists():
        stored = serialization.load_pem_public_key(public_path.read_bytes())
        if stored.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo) != public:
            raise ValueError('The issuer private key does not match the application public key.')
    if not public_path.exists():
        atomic_write(public_path, public.decode('ascii'))
    return key


def issue_license(ipv4, days, private_path=PRIVATE_KEY_PATH, public_path=PUBLIC_KEY_PATH, now=None):
    address = ipaddress.IPv4Address(ipv4)
    if address.is_loopback or address.is_unspecified or address.is_multicast:
        raise ValueError('Choose a usable local IPv4 address.')
    if type(days) is not int or not 1 <= days <= 36500:
        raise ValueError('Validity must be between 1 and 36500 whole days.')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('The issuance time must include a time zone.')
    payload = {'product': 'CircleCircle2', 'version': 1, 'ipv4': str(address),
               'issued_at': now.isoformat(), 'expires_at': (now + timedelta(days=days)).isoformat()}
    encoded = encode_bytes(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8'))
    key = signing_key(private_path, public_path)
    signature = key.sign(b'C2V1.' + encoded.encode('ascii'))
    return 'C2V1.' + encoded + '.' + encode_bytes(signature)
