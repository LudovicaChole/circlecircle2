import json
from pathlib import Path
from utilities.error_messages import error_message
from utilities.app_paths import config_directory
from utilities.licensing import atomic_write


class ProfileSettings:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config_directory() / 'profile.setting'

    def preferences(self):
        from utilities.app_paths import application_directory
        defaults = {'material_library_path': str(application_directory()),
                    'unit': 'kg/mm/ms/J', 'word_wrap': False, 'font_size': 10}
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                defaults.update({key: data[key] for key in defaults if key in data})
        except (OSError, ValueError):
            pass
        from core.fea.material_units import model_unit
        defaults['unit'] = model_unit(defaults['unit'])
        if type(defaults['word_wrap']) is not bool:
            defaults['word_wrap'] = False
        if type(defaults['font_size']) is not int or not 6 <= defaults['font_size'] <= 48:
            defaults['font_size'] = 10
        if not isinstance(defaults['material_library_path'], str):
            from utilities.app_paths import application_directory
            defaults['material_library_path'] = str(application_directory())
        return defaults

    def save_preferences(self, **values):
        data = {}
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                data = {}
        except (OSError, ValueError):
            pass
        data.update(values)
        atomic_write(self.path, json.dumps(data, ensure_ascii=False, indent=2))

    def work_directory(self):
        if not self.path.exists():
            return None
        try:
            value = json.loads(self.path.read_text(encoding='utf-8'))['work_directory']
            if not isinstance(value, str) or not Path(value).is_dir():
                raise ValueError('The saved work directory is unavailable.')
            return str(Path(value).resolve())
        except (OSError, ValueError, KeyError, TypeError) as error:
            from utilities.logger import logger
            logger.warning(f'Cannot restore work directory from {self.path}: {error_message(error)}')
            return None

    def save_work_directory(self, directory):
        directory = Path(directory).resolve(strict=True)
        if not directory.is_dir():
            raise ValueError('The work directory must be a folder.')
        data = {}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding='utf-8'))
                if not isinstance(data, dict):
                    data = {}
            except (OSError, ValueError):
                pass
        data['work_directory'] = str(directory)
        data.pop('log_directory', None)
        atomic_write(self.path, json.dumps(data, ensure_ascii=False, indent=2))
