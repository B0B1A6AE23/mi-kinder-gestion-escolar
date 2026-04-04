"""Rutas de autenticacion."""
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from mi_kinder_web.app import get_db
from mi_kinder_web.models import WebUser

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember_me"))

        if not username or not password:
            flash("Ingresa usuario y contrasena.", "error")
            return render_template("login.html")

        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
        ).fetchone()

        if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
            user = WebUser(row)
            login_user(user, remember=remember)
            session.permanent = True
            flash(f"Bienvenida, {user.full_name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        else:
            flash("Usuario o contrasena incorrectos.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesion cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
