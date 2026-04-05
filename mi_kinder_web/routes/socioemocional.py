"""Rutas de seguimiento socioemocional (observaciones)."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

socio_bp = Blueprint("socioemocional", __name__)


@socio_bp.route("/socioemocional")
@login_required
def index():
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    periods = db.execute(
        "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    selected_group = request.args.get("group_id", type=int)
    selected_period = request.args.get("period_id", type=int)

    students = []
    observations_map = {}

    if selected_group:
        students = db.execute(
            """SELECT s.id, s.first_name, s.last_name, s.second_last_name
               FROM students s
               WHERE s.group_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name""",
            (selected_group,),
        ).fetchall()

        for student in students:
            if selected_period:
                obs = db.execute(
                    """SELECT so.*, u.full_name as author_name
                       FROM student_observations so
                       LEFT JOIN users u ON u.id = so.created_by
                       WHERE so.student_id = ? AND so.period_id = ?
                       ORDER BY so.created_at DESC""",
                    (student["id"], selected_period),
                ).fetchall()
            else:
                obs = db.execute(
                    """SELECT so.*, u.full_name as author_name
                       FROM student_observations so
                       LEFT JOIN users u ON u.id = so.created_by
                       WHERE so.student_id = ?
                       ORDER BY so.created_at DESC LIMIT 10""",
                    (student["id"],),
                ).fetchall()
            observations_map[student["id"]] = obs

    return render_template(
        "socioemocional.html",
        groups=groups,
        periods=periods,
        students=students,
        observations_map=observations_map,
        selected_group=selected_group,
        selected_period=selected_period,
    )


@socio_bp.route("/socioemocional/add", methods=["POST"])
@login_required
def add_observation():
    db = get_db()
    student_id = request.form.get("student_id", type=int)
    period_id = request.form.get("period_id", type=int)
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "general")
    group_id = request.form.get("group_id", type=int)

    if not student_id or not content:
        flash("El alumno y el contenido son obligatorios.", "error")
        return redirect(url_for("socioemocional.index", group_id=group_id, period_id=period_id))

    db.execute(
        """INSERT INTO student_observations (student_id, period_id, content, category, created_by)
           VALUES (?, ?, ?, ?, ?)""",
        (student_id, period_id, content, category, current_user.id),
    )
    db.commit()

    flash("Observación registrada.", "success")
    return redirect(url_for("socioemocional.index", group_id=group_id, period_id=period_id))


@socio_bp.route("/socioemocional/<int:obs_id>/delete", methods=["POST"])
@login_required
def delete_observation(obs_id):
    db = get_db()
    group_id = request.form.get("group_id", type=int)
    period_id = request.form.get("period_id", type=int)

    obs = db.execute(
        "SELECT * FROM student_observations WHERE id = ?", (obs_id,)
    ).fetchone()
    if not obs:
        flash("Observación no encontrada.", "error")
        return redirect(url_for("socioemocional.index"))

    # Only author or directora can delete
    if current_user.role != "directora" and obs["created_by"] != current_user.id:
        flash("No tienes permiso para eliminar esta observación.", "error")
        return redirect(url_for("socioemocional.index", group_id=group_id, period_id=period_id))

    db.execute("DELETE FROM student_observations WHERE id = ?", (obs_id,))
    db.commit()
    flash("Observación eliminada.", "success")
    return redirect(url_for("socioemocional.index", group_id=group_id, period_id=period_id))
