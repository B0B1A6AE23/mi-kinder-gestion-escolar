"""Datos iniciales para la base de datos."""
import sqlite3
import bcrypt


def seed_database(conn: sqlite3.Connection):
    """Inserta datos iniciales si no existen."""
    _seed_admin_user(conn)
    _seed_default_grading_scale(conn)
    _seed_school_info(conn)
    conn.commit()


def _seed_admin_user(conn: sqlite3.Connection):
    """Crea la cuenta de directora por defecto."""
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", ("directora",)
    ).fetchone()
    if row:
        return

    password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    conn.execute(
        """INSERT INTO users (username, password_hash, full_name, role)
           VALUES (?, ?, ?, ?)""",
        ("directora", password_hash, "Directora", "directora"),
    )


def _seed_default_grading_scale(conn: sqlite3.Connection):
    """Crea la escala de evaluacion por defecto."""
    row = conn.execute(
        "SELECT id FROM grading_scales WHERE is_default = 1"
    ).fetchone()
    if row:
        return

    cursor = conn.execute(
        """INSERT INTO grading_scales (name, scale_type, is_default)
           VALUES (?, ?, ?)""",
        ("Logros de Aprendizaje", "label", 1),
    )
    scale_id = cursor.lastrowid

    levels = [
        ("Logrado", 3.0, "#4CAF50", 1),
        ("En Proceso", 2.0, "#FFC107", 2),
        ("Requiere Apoyo", 1.0, "#FF5722", 3),
    ]
    for label, numeric_value, color, sort_order in levels:
        conn.execute(
            """INSERT INTO grading_scale_levels
               (grading_scale_id, label, numeric_value, color, sort_order)
               VALUES (?, ?, ?, ?, ?)""",
            (scale_id, label, numeric_value, color, sort_order),
        )


def _seed_school_info(conn: sqlite3.Connection):
    """Crea el registro singleton de informacion escolar."""
    conn.execute(
        "INSERT OR IGNORE INTO school_info (id, name) VALUES (1, 'Mi Kinder')"
    )
