"""Schema SQL completo para Mi Kinder."""

SCHEMA_SQL = """
-- ============================================================
-- SISTEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS db_migrations (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

CREATE TABLE IF NOT EXISTS school_info (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    name            TEXT NOT NULL DEFAULT 'Mi Kinder',
    address         TEXT,
    phone           TEXT,
    email           TEXT,
    logo_path       TEXT,
    director_name   TEXT,
    current_year_id INTEGER REFERENCES school_years(id)
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- ============================================================
-- AUTENTICACION Y USUARIOS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('directora', 'maestra')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- CICLO ESCOLAR Y PERIODOS
-- ============================================================

CREATE TABLE IF NOT EXISTS school_years (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date   TEXT NOT NULL,
    is_active  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS periods (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    school_year_id INTEGER NOT NULL REFERENCES school_years(id),
    name           TEXT NOT NULL,
    start_date     TEXT NOT NULL,
    end_date       TEXT NOT NULL,
    sort_order     INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(school_year_id, name)
);

-- ============================================================
-- GRUPOS
-- ============================================================

CREATE TABLE IF NOT EXISTS groups_ (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    school_year_id INTEGER NOT NULL REFERENCES school_years(id),
    name           TEXT NOT NULL,
    grade_level    TEXT,
    capacity       INTEGER,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(school_year_id, name)
);

CREATE TABLE IF NOT EXISTS user_group_assignments (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL REFERENCES users(id),
    group_id INTEGER NOT NULL REFERENCES groups_(id),
    UNIQUE(user_id, group_id)
);

-- ============================================================
-- ALUMNOS
-- ============================================================

CREATE TABLE IF NOT EXISTS students (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id         INTEGER NOT NULL REFERENCES groups_(id),
    first_name       TEXT NOT NULL,
    last_name        TEXT NOT NULL,
    second_last_name TEXT,
    curp             TEXT,
    birth_date       TEXT,
    gender           TEXT CHECK (gender IN ('M', 'F', NULL)),
    photo_path       TEXT,
    enrollment_date  TEXT NOT NULL DEFAULT (date('now')),
    guardian_name    TEXT,
    guardian_phone   TEXT,
    guardian_email   TEXT,
    address          TEXT,
    blood_type       TEXT,
    allergies        TEXT,
    medical_notes    TEXT,
    is_active        INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_students_group ON students(group_id);
CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);

CREATE TABLE IF NOT EXISTS student_transfers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id     INTEGER NOT NULL REFERENCES students(id),
    from_group_id  INTEGER NOT NULL REFERENCES groups_(id),
    to_group_id    INTEGER NOT NULL REFERENCES groups_(id),
    transfer_date  TEXT NOT NULL DEFAULT (date('now')),
    reason         TEXT,
    transferred_by INTEGER REFERENCES users(id),
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- SISTEMA DE EVALUACION
-- ============================================================

CREATE TABLE IF NOT EXISTS grading_scales (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    scale_type     TEXT NOT NULL CHECK (scale_type IN ('numeric', 'letter', 'label')),
    school_year_id INTEGER REFERENCES school_years(id),
    is_default     INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS grading_scale_levels (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    grading_scale_id INTEGER NOT NULL REFERENCES grading_scales(id) ON DELETE CASCADE,
    label            TEXT NOT NULL,
    numeric_value    REAL,
    color            TEXT,
    sort_order       INTEGER NOT NULL DEFAULT 0,
    UNIQUE(grading_scale_id, label)
);

CREATE TABLE IF NOT EXISTS evaluation_areas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    school_year_id INTEGER NOT NULL REFERENCES school_years(id),
    name           TEXT NOT NULL,
    description    TEXT,
    sort_order     INTEGER NOT NULL DEFAULT 0,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(school_year_id, name)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id         INTEGER NOT NULL REFERENCES students(id),
    evaluation_area_id INTEGER NOT NULL REFERENCES evaluation_areas(id),
    period_id          INTEGER NOT NULL REFERENCES periods(id),
    grading_scale_id   INTEGER NOT NULL REFERENCES grading_scales(id),
    grade_level_id     INTEGER REFERENCES grading_scale_levels(id),
    numeric_value      REAL,
    observations       TEXT,
    evaluated_by       INTEGER REFERENCES users(id),
    evaluated_at       TEXT NOT NULL DEFAULT (datetime('now')),
    created_at         TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at         TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(student_id, evaluation_area_id, period_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_student ON evaluations(student_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_period ON evaluations(period_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_area ON evaluations(evaluation_area_id);

-- ============================================================
-- OBSERVACIONES Y ASISTENCIA
-- ============================================================

CREATE TABLE IF NOT EXISTS student_observations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    period_id   INTEGER REFERENCES periods(id),
    content     TEXT NOT NULL,
    category    TEXT DEFAULT 'general',
    created_by  INTEGER REFERENCES users(id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS attendance_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    date        TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('present', 'absent', 'late', 'justified')),
    notes       TEXT,
    recorded_by INTEGER REFERENCES users(id),
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(student_id, date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance_records(date);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance_records(student_id);

-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id),
    action      TEXT NOT NULL,
    table_name  TEXT NOT NULL,
    record_id   INTEGER,
    old_values  TEXT,
    new_values  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""
