"""App Flask para Mi Kinder -- reutiliza backend existente."""
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, g
from flask_login import LoginManager

from mi_kinder_web.config import (
    DB_PATH, SECRET_KEY, DATA_DIR,
    PERMANENT_SESSION_LIFETIME, REMEMBER_COOKIE_DURATION,
    SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE,
)
from mi_kinder.database.schema import SCHEMA_SQL
from mi_kinder.database.migrations import run_migrations
from mi_kinder.database.seed import seed_database


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        from mi_kinder_web.utils import unaccent
        g.db = sqlite3.connect(DB_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
        g.db.execute("PRAGMA busy_timeout=5000")
        g.db.create_function("unaccent", 1, unaccent)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    run_migrations(conn)
    seed_database(conn)
    conn.close()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["PERMANENT_SESSION_LIFETIME"] = PERMANENT_SESSION_LIFETIME
    app.config["REMEMBER_COOKIE_DURATION"] = REMEMBER_COOKIE_DURATION
    app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = SESSION_COOKIE_SAMESITE

    init_db()
    app.teardown_appcontext(close_db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesion para continuar."

    @login_manager.user_loader
    def load_user(user_id):
        from mi_kinder_web.models import WebUser
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE id = ?", (int(user_id),)
        ).fetchone()
        if row:
            return WebUser(row)
        return None

    # Template filters
    from datetime import datetime

    @app.template_filter("fecha_mx")
    def fecha_mx_filter(value):
        if not value:
            return ""
        try:
            dt = datetime.strptime(str(value), "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return str(value)

    @app.template_filter("status_label")
    def status_label_filter(value):
        labels = {
            "present": "Presente",
            "absent": "Falta",
            "late": "Retardo",
            "justified": "Justificada",
        }
        return labels.get(value, value)

    # Context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        db = get_db()
        active_year = db.execute(
            "SELECT * FROM school_years WHERE is_active = 1"
        ).fetchone()
        current_period = None
        if active_year:
            current_period = db.execute(
                "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order DESC LIMIT 1",
                (active_year["id"],),
            ).fetchone()
        return dict(
            app_name="Colegio CAPI",
            active_year=active_year,
            current_period=current_period,
            is_directora=current_user.is_authenticated and current_user.role == "directora",
        )

    # Register blueprints
    from mi_kinder_web.routes.auth import auth_bp
    from mi_kinder_web.routes.dashboard import dashboard_bp
    from mi_kinder_web.routes.groups import groups_bp
    from mi_kinder_web.routes.students import students_bp
    from mi_kinder_web.routes.users import users_bp
    from mi_kinder_web.routes.attendance import attendance_bp
    from mi_kinder_web.routes.evaluations import evaluations_bp
    from mi_kinder_web.routes.settings import settings_bp
    from mi_kinder_web.routes.charts import charts_bp
    from mi_kinder_web.routes.reports import reports_bp
    from mi_kinder_web.routes.socioemocional import socio_bp
    from mi_kinder_web.routes.profile import profile_bp
    from mi_kinder_web.routes.exports import exports_bp
    from mi_kinder_web.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(evaluations_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(socio_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(api_bp)

    return app
