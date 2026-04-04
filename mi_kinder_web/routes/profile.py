"""Rutas de perfil de usuario."""
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def index():
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (current_user.id,)
    ).fetchone()

    groups = db.execute(
        """SELECT g.name FROM user_group_assignments uga
           JOIN groups_ g ON g.id = uga.group_id
           WHERE uga.user_id = ? AND g.is_active = 1
           ORDER BY g.name""",
        (current_user.id,),
    ).fetchall()

    return render_template("profile.html", user=user, groups=groups)


@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def update():
    db = get_db()
    full_name = request.form.get("full_name", "").strip()
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if full_name:
        db.execute(
            "UPDATE users SET full_name=?, updated_at=datetime('now') WHERE id=?",
            (full_name, current_user.id),
        )

    if new_password:
        if not current_password:
            flash("Ingresa tu contrasena actual.", "error")
            return redirect(url_for("profile.index"))

        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (current_user.id,)
        ).fetchone()

        if not bcrypt.checkpw(current_password.encode(), user["password_hash"].encode()):
            flash("Contrasena actual incorrecta.", "error")
            return redirect(url_for("profile.index"))

        if new_password != confirm_password:
            flash("Las contrasenas nuevas no coinciden.", "error")
            return redirect(url_for("profile.index"))

        if len(new_password) < 4:
            flash("La contrasena debe tener al menos 4 caracteres.", "error")
            return redirect(url_for("profile.index"))

        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        db.execute(
            "UPDATE users SET password_hash=?, updated_at=datetime('now') WHERE id=?",
            (password_hash, current_user.id),
        )
        flash("Contrasena actualizada.", "success")

    db.commit()
    if full_name and not new_password:
        flash("Perfil actualizado.", "success")
    return redirect(url_for("profile.index"))
