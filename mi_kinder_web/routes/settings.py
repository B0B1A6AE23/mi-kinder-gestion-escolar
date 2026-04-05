"""Rutas de ajustes del sistema."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
@login_required
def index():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    school_info = db.execute("SELECT * FROM school_info WHERE id = 1").fetchone()
    school_years = db.execute(
        "SELECT * FROM school_years ORDER BY start_date DESC"
    ).fetchall()

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    periods = []
    areas = []
    if year_id:
        periods = db.execute(
            "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
            (year_id,),
        ).fetchall()
        areas = db.execute(
            "SELECT * FROM evaluation_areas WHERE school_year_id = ? ORDER BY sort_order",
            (year_id,),
        ).fetchall()

    # Grading scales
    scales = db.execute("SELECT * FROM grading_scales ORDER BY name").fetchall()
    scale_levels = {}
    for s in scales:
        levels = db.execute(
            "SELECT * FROM grading_scale_levels WHERE grading_scale_id = ? ORDER BY sort_order",
            (s["id"],),
        ).fetchall()
        scale_levels[s["id"]] = levels

    return render_template(
        "settings.html",
        school_info=school_info,
        school_years=school_years,
        periods=periods,
        areas=areas,
        scales=scales,
        scale_levels=scale_levels,
    )


@settings_bp.route("/settings/school-info", methods=["POST"])
@login_required
def update_school_info():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    director_name = request.form.get("director_name", "").strip()

    db.execute(
        """UPDATE school_info SET name=?, address=?, phone=?, email=?, director_name=?
           WHERE id = 1""",
        (name or "Colegio CAPI", address or None, phone or None,
         email or None, director_name or None),
    )
    db.commit()
    flash("Información escolar actualizada.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/school-year", methods=["POST"])
@login_required
def create_school_year():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    name = request.form.get("name", "").strip()
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    set_active = bool(request.form.get("set_active"))

    if not name or not start_date or not end_date:
        flash("Todos los campos del ciclo escolar son obligatorios.", "error")
        return redirect(url_for("settings.index"))

    if set_active:
        db.execute("UPDATE school_years SET is_active = 0")

    db.execute(
        """INSERT INTO school_years (name, start_date, end_date, is_active)
           VALUES (?, ?, ?, ?)""",
        (name, start_date, end_date, int(set_active)),
    )

    if set_active:
        year_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.execute(
            "UPDATE school_info SET current_year_id = ? WHERE id = 1",
            (year_id,),
        )

    db.commit()
    flash(f"Ciclo escolar '{name}' creado.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/school-year/<int:year_id>/activate", methods=["POST"])
@login_required
def activate_school_year(year_id):
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    db.execute("UPDATE school_years SET is_active = 0")
    db.execute("UPDATE school_years SET is_active = 1 WHERE id = ?", (year_id,))
    db.execute("UPDATE school_info SET current_year_id = ? WHERE id = 1", (year_id,))
    db.commit()
    flash("Ciclo escolar activado.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/period", methods=["POST"])
@login_required
def create_period():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    if not active_year:
        flash("No hay ciclo escolar activo.", "error")
        return redirect(url_for("settings.index"))

    name = request.form.get("name", "").strip()
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")
    sort_order = request.form.get("sort_order", type=int, default=0)

    if not name or not start_date or not end_date:
        flash("Todos los campos del periodo son obligatorios.", "error")
        return redirect(url_for("settings.index"))

    db.execute(
        """INSERT INTO periods (school_year_id, name, start_date, end_date, sort_order)
           VALUES (?, ?, ?, ?, ?)""",
        (active_year["id"], name, start_date, end_date, sort_order),
    )
    db.commit()
    flash(f"Periodo '{name}' creado.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/area", methods=["POST"])
@login_required
def create_area():
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    if not active_year:
        flash("No hay ciclo escolar activo.", "error")
        return redirect(url_for("settings.index"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    sort_order = request.form.get("sort_order", type=int, default=0)

    if not name:
        flash("El nombre del área es obligatorio.", "error")
        return redirect(url_for("settings.index"))

    db.execute(
        """INSERT INTO evaluation_areas (school_year_id, name, description, sort_order, is_active)
           VALUES (?, ?, ?, ?, 1)""",
        (active_year["id"], name, description or None, sort_order),
    )
    db.commit()
    flash(f"Área de evaluación '{name}' creada.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/area/<int:area_id>/edit", methods=["POST"])
@login_required
def edit_area(area_id):
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    area = db.execute(
        "SELECT * FROM evaluation_areas WHERE id = ?", (area_id,)
    ).fetchone()
    if not area:
        flash("Área no encontrada.", "error")
        return redirect(url_for("settings.index"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    sort_order = request.form.get("sort_order", type=int, default=area["sort_order"])

    if not name:
        flash("El nombre del área es obligatorio.", "error")
        return redirect(url_for("settings.index"))

    db.execute(
        "UPDATE evaluation_areas SET name=?, description=?, sort_order=? WHERE id=?",
        (name, description or None, sort_order, area_id),
    )
    db.commit()
    flash(f"Área '{name}' actualizada.", "success")
    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/area/<int:area_id>/delete", methods=["POST"])
@login_required
def delete_area(area_id):
    if current_user.role != "directora":
        flash("Acceso restringido.", "error")
        return redirect(url_for("dashboard.index"))

    db = get_db()
    area = db.execute(
        "SELECT * FROM evaluation_areas WHERE id = ?", (area_id,)
    ).fetchone()
    if not area:
        flash("Área no encontrada.", "error")
        return redirect(url_for("settings.index"))

    # Check if there are evaluations using this area
    eval_count = db.execute(
        "SELECT COUNT(*) as cnt FROM evaluations WHERE evaluation_area_id = ?",
        (area_id,),
    ).fetchone()["cnt"]

    if eval_count > 0:
        # Soft-delete: mark inactive so history is preserved
        db.execute(
            "UPDATE evaluation_areas SET is_active=0 WHERE id=?", (area_id,)
        )
        db.commit()
        flash(
            f"Área desactivada (tiene {eval_count} evaluaciones registradas — los datos históricos se conservan).",
            "warning",
        )
    else:
        # Hard-delete: no evaluations, safe to remove
        db.execute("DELETE FROM evaluation_areas WHERE id=?", (area_id,))
        db.commit()
        flash("Área eliminada.", "success")

    return redirect(url_for("settings.index"))
