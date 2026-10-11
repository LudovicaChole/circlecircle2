import logging
from pathlib import Path
from utilities.source_location import diagnostic


class Logger:
    def __init__(self, log_file=None):
        self.logger = logging.getLogger('user_logger')
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
        self.file_handler = None
        if log_file:
            self.configure_file(log_file)

    def configure_file(self, path):
        path = Path(path).resolve()
        if self.file_handler and Path(self.file_handler.baseFilename) == path:
            return True
        self.close_file()
        try:
            handler = logging.FileHandler(path, mode='a', encoding='utf-8')
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
            self.file_handler = handler
            return True
        except OSError:
            self.logger.warning('Cannot write to the current work directory. Check its availability and write permissions. Console logging remains available.')
            return False

    def close_file(self):
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None

    def configure_profile(self, profile, warn=True):
        directory = profile.work_directory()
        if directory:
            return self.configure_file(Path(directory) / 'app.log')
        self.close_file()
        if warn:
            self.logger.warning('Please set a work directory using File > Set Work Directory to enable file logging.')
        return False

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg, source=None):
        self.logger.warning(diagnostic(msg, source))

    def error(self, msg, source=None):
        self.logger.error(diagnostic(msg, source))

    def critical(self, msg, source=None):
        self.logger.critical(diagnostic(msg, source))


logger = Logger()
