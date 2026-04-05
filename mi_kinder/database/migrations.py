"""Sistema de migraciones para la base de datos."""
import sqlite3
from mi_kinder.database.schema import SCHEMA_SQL

CURRENT_VERSION = 2


def run_migrations(conn: sqlite3.Connection):
    """Ejecuta migraciones pendientes en la base de datos."""
    conn.executescript(SCHEMA_SQL)

    row = conn.execute(
        "SELECT MAX(version) as v FROM db_migrations"
    ).fetchone()
    current = row["v"] if row and row["v"] else 0

    migrations = _get_migrations()
    for version, description, sql in migrations:
        if version > current:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO db_migrations (version, description) VALUES (?, ?)",
                (version, description),
            )
            conn.commit()

    if current == 0:
        conn.execute(
            "INSERT OR IGNORE INTO db_migrations (version, description) VALUES (?, ?)",
            (CURRENT_VERSION, "Schema inicial"),
        )
        conn.commit()


def _get_migrations() -> list[tuple[int, str, str]]:
    """Retorna lista de (version, descripcion, sql) para migraciones futuras."""
    return [
        (
            2,
            "Agregar foto de perfil a usuarios y foto de tutor a alumnos",
            """
ALTER TABLE users ADD COLUMN photo_path TEXT;
ALTER TABLE students ADD COLUMN guardian_photo_path TEXT;
""",
        ),
    ]
