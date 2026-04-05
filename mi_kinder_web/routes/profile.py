"""Rutas de perfil de usuario."""
import os
import uuid
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from mi_kinder_web.app import get_db
from mi_kinder_web.config import PHOTOS_DIR

profile_bp = Blueprint("profile", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
            flash("Ingresa tu contraseña actual.", "error")
            return redirect(url_for("profile.index"))

        user = db.execute(
            "SELECT * FROM users WHERE id = ?", (current_user.id,)
        ).fetchone()

        if not bcrypt.checkpw(current_password.encode(), user["password_hash"].encode()):
            flash("Contraseña actual incorrecta.", "error")
            return redirect(url_for("profile.index"))

        if new_password != confirm_password:
            flash("Las contraseñas nuevas no coinciden.", "error")
            return redirect(url_for("profile.index"))

        if len(new_password) < 4:
            flash("La contraseña debe tener al menos 4 caracteres.", "error")
            return redirect(url_for("profile.index"))

        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        db.execute(
            "UPDATE users SET password_hash=?, updated_at=datetime('now') WHERE id=?",
            (password_hash, current_user.id),
        )
        flash("Contraseña actualizada.", "success")

    # Handle profile photo upload
    if "photo" in request.files:
        photo = request.files["photo"]
        if photo.filename and allowed_file(photo.filename):
            ext = photo.filename.rsplit(".", 1)[1].lower()
            filename = f"user_{uuid.uuid4().hex}.{ext}"
            photo.save(os.path.join(PHOTOS_DIR, filename))
            db.execute(
                "UPDATE users SET photo_path=?, updated_at=datetime('now') WHERE id=?",
                (filename, current_user.id),
            )
            flash("Foto de perfil actualizada.", "success")
        elif photo.filename:
            flash("Formato de imagen no válido. Usa JPG, PNG, GIF o WEBP.", "error")

    db.commit()
    if full_name and not new_password:
        flash("Perfil actualizado.", "success")
    return redirect(url_for("profile.index"))


@profile_bp.route("/profile/photo/delete", methods=["POST"])
@login_required
def delete_photo():
    db = get_db()
    db.execute(
        "UPDATE users SET photo_path=NULL, updated_at=datetime('now') WHERE id=?",
        (current_user.id,),
    )
    db.commit()
    flash("Foto eliminada.", "success")
    return redirect(url_for("profile.index"))
