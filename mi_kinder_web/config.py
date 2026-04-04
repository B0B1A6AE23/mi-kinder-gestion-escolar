"""Configuracion del servidor web."""
import os
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "MiKinder")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "mi_kinder.db")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

_SECRET_FILE = os.path.join(DATA_DIR, ".flask_secret")
if os.path.isfile(_SECRET_FILE):
    with open(_SECRET_FILE) as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = secrets.token_hex(32)
    with open(_SECRET_FILE, "w") as f:
        f.write(SECRET_KEY)

from datetime import timedelta
PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
REMEMBER_COOKIE_DURATION = timedelta(days=7)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
