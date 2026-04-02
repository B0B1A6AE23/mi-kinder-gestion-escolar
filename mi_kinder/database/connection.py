"""Administrador de conexion SQLite singleton."""
import sqlite3
import threading
from mi_kinder.config import get_db_path

_lock = threading.Lock()
_connection: sqlite3.Connection | None = None


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Retorna la conexion singleton a SQLite. Thread-safe."""
    global _connection
    with _lock:
        if _connection is None:
            path = db_path or get_db_path()
            _connection = sqlite3.connect(path, check_same_thread=False)
            _connection.row_factory = sqlite3.Row
            _connection.execute("PRAGMA journal_mode=WAL")
            _connection.execute("PRAGMA foreign_keys=ON")
            _connection.execute("PRAGMA busy_timeout=5000")
        return _connection


def close_connection():
    """Cierra la conexion singleton."""
    global _connection
    with _lock:
        if _connection is not None:
            _connection.close()
            _connection = None


def get_memory_connection() -> sqlite3.Connection:
    """Retorna una conexion en memoria para tests."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
