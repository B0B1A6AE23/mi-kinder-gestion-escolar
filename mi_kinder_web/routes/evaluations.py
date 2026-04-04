"""Rutas de evaluaciones."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

evaluations_bp = Blueprint("evaluations", __name__)


@evaluations_bp.route("/evaluations")
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

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1 ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    selected_group = request.args.get("group_id", type=int)
    selected_period = request.args.get("period_id", type=int)

    students = []
    evaluations_map = {}
    scale_levels = []

    if selected_group and selected_period:
        students = db.execute(
            """SELECT s.id, s.first_name, s.last_name, s.second_last_name
               FROM students s
               WHERE s.group_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name""",
            (selected_group,),
        ).fetchall()

        # Get default grading scale
        scale = db.execute(
            "SELECT * FROM grading_scales WHERE is_default = 1"
        ).fetchone()
        if scale:
            scale_levels = db.execute(
                "SELECT * FROM grading_scale_levels WHERE grading_scale_id = ? ORDER BY sort_order",
                (scale["id"],),
            ).fetchall()

        # Get existing evaluations
        evals = db.execute(
            """SELECT e.student_id, e.evaluation_area_id, e.grade_level_id,
                      e.numeric_value, e.observations,
                      gsl.label as grade_label, gsl.color as grade_color
               FROM evaluations e
               LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
               WHERE e.period_id = ?
                 AND e.student_id IN (
                     SELECT id FROM students WHERE group_id = ? AND is_active = 1
                 )""",
            (selected_period, selected_group),
        ).fetchall()

        for ev in evals:
            key = (ev["student_id"], ev["evaluation_area_id"])
            evaluations_map[key] = {
                "grade_level_id": ev["grade_level_id"],
                "numeric_value": ev["numeric_value"],
                "observations": ev["observations"] or "",
                "grade_label": ev["grade_label"] or "",
                "grade_color": ev["grade_color"] or "",
            }

    return render_template(
        "evaluations.html",
        groups=groups,
        periods=periods,
        areas=areas,
        students=students,
        evaluations_map=evaluations_map,
        scale_levels=scale_levels,
        selected_group=selected_group,
        selected_period=selected_period,
    )


@evaluations_bp.route("/evaluations/save", methods=["POST"])
@login_required
def save():
    db = get_db()
    group_id = request.form.get("group_id", type=int)
    period_id = request.form.get("period_id", type=int)

    if not group_id or not period_id:
        flash("Selecciona grupo y periodo.", "error")
        return redirect(url_for("evaluations.index"))

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1",
        (year_id,),
    ).fetchall()

    scale = db.execute(
        "SELECT * FROM grading_scales WHERE is_default = 1"
    ).fetchone()
    scale_id = scale["id"] if scale else 1

    students = db.execute(
        "SELECT id FROM students WHERE group_id = ? AND is_active = 1",
        (group_id,),
    ).fetchall()

    count = 0
    for student in students:
        sid = student["id"]
        for area in areas:
            aid = area["id"]
            grade_level_id = request.form.get(f"grade_{sid}_{aid}", type=int)
            observations = request.form.get(f"obs_{sid}_{aid}", "").strip()

            if grade_level_id:
                # Get numeric value from the level
                level = db.execute(
                    "SELECT numeric_value FROM grading_scale_levels WHERE id = ?",
                    (grade_level_id,),
                ).fetchone()
                numeric_value = level["numeric_value"] if level else None

                existing = db.execute(
                    """SELECT id FROM evaluations
                       WHERE student_id = ? AND evaluation_area_id = ? AND period_id = ?""",
                    (sid, aid, period_id),
                ).fetchone()

                if existing:
                    db.execute(
                        """UPDATE evaluations SET grading_scale_id=?, grade_level_id=?,
                           numeric_value=?, observations=?, evaluated_by=?,
                           evaluated_at=datetime('now'), updated_at=datetime('now')
                           WHERE id=?""",
                        (scale_id, grade_level_id, numeric_value,
                         observations or None, current_user.id, existing["id"]),
                    )
                else:
                    db.execute(
                        """INSERT INTO evaluations (student_id, evaluation_area_id, period_id,
                           grading_scale_id, grade_level_id, numeric_value, observations, evaluated_by)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (sid, aid, period_id, scale_id, grade_level_id,
                         numeric_value, observations or None, current_user.id),
                    )
                count += 1

    db.commit()
    flash(f"Se guardaron {count} evaluaciones.", "success")
    return redirect(
        url_for("evaluations.index", group_id=group_id, period_id=period_id)
    )
