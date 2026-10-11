"""Application-owned paths, independent of the selected work directory."""
import sys
from pathlib import Path


def application_directory():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def config_directory():
    return application_directory() / 'config'


def resource_directory():
    """Read-only resources live inside the bundle, while config stays beside the EXE."""
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
