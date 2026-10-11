"""Persistent towing conversion settings, separate from the user's work directory."""
from pathlib import Path
import json
import math
from utilities.app_paths import config_directory
from utilities.licensing import atomic_write


def model_path(kind):
    if kind not in ('hook', 'towing'):
        raise ValueError('Unknown towing model kind')
    return config_directory() / f'towing_{kind}_pointnet.pt'


def load(path=None):
    path = Path(path) if path else config_directory() / 'abaqus_translate.json'
    data = {'enabled': True, 'length': 300.0, 'template': ''}
    if path.exists():
        record = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(record, dict):
            raise ValueError('Towing settings must be a JSON object.')
        data.update({key: record[key] for key in data if key in record})
    validate(data)
    return data


def validate(data):
    if type(data['enabled']) is not bool or not isinstance(data['template'], str):
        raise ValueError('Invalid towing settings.')
    try:
        length = float(data['length'])
    except (TypeError, ValueError) as error:
        raise ValueError('Towing L must be a number.') from error
    if not math.isfinite(length) or length == 0:
        raise ValueError('Towing L must be finite and nonzero.')
    if data['template'] and Path(data['template']).suffix.lower() not in ('.inp', '.geo'):
        raise ValueError('Select an Abaqus .inp or mesh .geo template.')


def save(data, path=None):
    validate(data)
    target = Path(path) if path else config_directory() / 'abaqus_translate.json'
    atomic_write(target, json.dumps(data, ensure_ascii=False, indent=2))
