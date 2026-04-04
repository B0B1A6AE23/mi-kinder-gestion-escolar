"""Rutas de gestion de usuarios."""
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
@login_required
def index():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    users = db.execute(
        "SELECT * FROM users ORDER BY role, full_name"
    ).fetchall()

    # Get group assignments for each user
    user_groups = {}
    for user in users:
        groups = db.execute(
            """SELECT g.name FROM user_group_assignments uga
               JOIN groups_ g ON g.id = uga.group_id
               WHERE uga.user_id = ? AND g.is_active = 1
               ORDER BY g.name""",
            (user["id"],),
        ).fetchall()
        user_groups[user["id"]] = [g["name"] for g in groups]

    return render_template("users.html", users=users, user_groups=user_groups)


@users_bp.route("/users/create", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "maestra")
        group_ids = request.form.getlist("group_ids")

        if not username or not password or not full_name:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("user_form.html", user=None, groups=groups)

        # Check unique username
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            flash("El nombre de usuario ya existe.", "error")
            return render_template("user_form.html", user=None, groups=groups)

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        db.execute(
            """INSERT INTO users (username, password_hash, full_name, role, is_active)
               VALUES (?, ?, ?, ?, 1)""",
            (username, password_hash, full_name, role),
        )
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Assign groups
        for gid in group_ids:
            db.execute(
                "INSERT OR IGNORE INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
                (user_id, int(gid)),
            )
        db.commit()

        flash(f"Usuario '{username}' creado exitosamente.", "success")
        return redirect(url_for("users.index"))

    return render_template("user_form.html", user=None, groups=groups)


@users_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit(user_id):
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("users.index"))

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    current_groups = [
        r["group_id"]
        for r in db.execute(
            "SELECT group_id FROM user_group_assignments WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    ]

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "maestra")
        password = request.form.get("password", "").strip()
        is_active = bool(request.form.get("is_active"))
        group_ids = request.form.getlist("group_ids")

        if not full_name:
            flash("El nombre es obligatorio.", "error")
            return render_template(
                "user_form.html", user=user, groups=groups, current_groups=current_groups
            )

        if password:
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            db.execute(
                """UPDATE users SET full_name=?, role=?, password_hash=?, is_active=?,
                   updated_at=datetime('now') WHERE id=?""",
                (full_name, role, password_hash, int(is_active), user_id),
            )
        else:
            db.execute(
                """UPDATE users SET full_name=?, role=?, is_active=?,
                   updated_at=datetime('now') WHERE id=?""",
                (full_name, role, int(is_active), user_id),
            )

        # Update group assignments
        db.execute(
            "DELETE FROM user_group_assignments WHERE user_id = ?", (user_id,)
        )
        for gid in group_ids:
            db.execute(
                "INSERT INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
                (user_id, int(gid)),
            )
        db.commit()

        flash(f"Usuario actualizado.", "success")
        return redirect(url_for("users.index"))

    return render_template(
        "user_form.html", user=user, groups=groups, current_groups=current_groups
    )
