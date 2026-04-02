"""Configuracion global de la aplicacion."""
import os
import sys

APP_NAME = "Mi Kinder"
APP_VERSION = "1.0.0"
DB_FILENAME = "mi_kinder.db"

def get_data_dir() -> str:
    """Retorna el directorio de datos de la aplicacion en %APPDATA%/MiKinder/."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.expanduser("~/.local/share")
    data_dir = os.path.join(base, "MiKinder")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_db_path() -> str:
    return os.path.join(get_data_dir(), DB_FILENAME)

def get_photos_dir() -> str:
    path = os.path.join(get_data_dir(), "photos")
    os.makedirs(path, exist_ok=True)
    return path

def get_exports_dir() -> str:
    path = os.path.join(get_data_dir(), "exports")
    os.makedirs(path, exist_ok=True)
    return path

def get_backups_dir() -> str:
    path = os.path.join(get_data_dir(), "backups")
    os.makedirs(path, exist_ok=True)
    return path
