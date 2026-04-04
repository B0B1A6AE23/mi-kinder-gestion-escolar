"""Rutas de reportes y boletas."""
import os
import tempfile
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required

from mi_kinder_web.app import get_db
from mi_kinder_web.config import EXPORTS_DIR

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
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

    return render_template("reports.html", groups=groups, periods=periods)


@reports_bp.route("/reports/individual/<int:student_id>")
@login_required
def individual(student_id):
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    student = db.execute(
        """SELECT s.*, g.name as group_name
           FROM students s
           JOIN groups_ g ON g.id = s.group_id
           WHERE s.id = ?""",
        (student_id,),
    ).fetchone()

    if not student:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("reports.index"))

    periods = db.execute(
        "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1 ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    evaluations = db.execute(
        """SELECT e.*, ea.name as area_name, p.name as period_name,
                  gsl.label as grade_label, gsl.color as grade_color
           FROM evaluations e
           JOIN evaluation_areas ea ON ea.id = e.evaluation_area_id
           JOIN periods p ON p.id = e.period_id
           LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
           WHERE e.student_id = ?
           ORDER BY p.sort_order, ea.sort_order""",
        (student_id,),
    ).fetchall()

    # Build eval table: (area_id, period_id) -> eval
    eval_table = {}
    for ev in evaluations:
        eval_table[(ev["evaluation_area_id"], ev["period_id"])] = ev

    observations = db.execute(
        """SELECT so.*, u.full_name as author_name
           FROM student_observations so
           LEFT JOIN users u ON u.id = so.created_by
           WHERE so.student_id = ?
           ORDER BY so.created_at DESC""",
        (student_id,),
    ).fetchall()

    return render_template(
        "report_individual.html",
        student=student,
        periods=periods,
        areas=areas,
        eval_table=eval_table,
        observations=observations,
    )


@reports_bp.route("/reports/individual/<int:student_id>/pdf")
@login_required
def individual_pdf(student_id):
    from mi_kinder.services.report_service import ReportService
    from mi_kinder.services.pdf_service import PDFService

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    report_svc = ReportService(db)
    data = report_svc.get_individual_report_data(student_id, year_id)

    if not data:
        flash("No se pudo generar el reporte.", "error")
        return redirect(url_for("reports.index"))

    student_name = data["student"].full_name.replace(" ", "_")
    filename = f"boleta_{student_name}.pdf"
    output_path = os.path.join(EXPORTS_DIR, filename)

    pdf_svc = PDFService()
    pdf_svc.generate_individual_report(data, output_path)

    return send_file(output_path, as_attachment=True, download_name=filename)


@reports_bp.route("/reports/group/<int:group_id>")
@login_required
def group(group_id):
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    group = db.execute(
        """SELECT g.*, u.full_name as teacher_name
           FROM groups_ g
           LEFT JOIN user_group_assignments uga ON uga.group_id = g.id
           LEFT JOIN users u ON u.id = uga.user_id
           WHERE g.id = ?""",
        (group_id,),
    ).fetchone()

    if not group:
        flash("Grupo no encontrado.", "error")
        return redirect(url_for("reports.index"))

    students = db.execute(
        """SELECT s.id, s.first_name || ' ' || s.last_name as full_name
           FROM students s
           WHERE s.group_id = ? AND s.is_active = 1
           ORDER BY s.last_name, s.first_name""",
        (group_id,),
    ).fetchall()

    periods = db.execute(
        "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1 ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    # Student averages
    student_averages = []
    for s in students:
        row = db.execute(
            """SELECT AVG(e.numeric_value) as avg_val
               FROM evaluations e
               WHERE e.student_id = ? AND e.numeric_value IS NOT NULL""",
            (s["id"],),
        ).fetchone()
        avg = round(row["avg_val"], 2) if row and row["avg_val"] else 0
        student_averages.append({
            "name": s["full_name"],
            "student_id": s["id"],
            "average": avg,
        })
    student_averages.sort(key=lambda x: x["average"], reverse=True)

    return render_template(
        "report_group.html",
        group=group,
        students=students,
        periods=periods,
        areas=areas,
        student_averages=student_averages,
    )


@reports_bp.route("/reports/group/<int:group_id>/pdf")
@login_required
def group_pdf(group_id):
    from mi_kinder.services.report_service import ReportService
    from mi_kinder.services.pdf_service import PDFService

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    report_svc = ReportService(db)
    data = report_svc.get_group_report_data(group_id, year_id)

    if not data:
        flash("No se pudo generar el reporte.", "error")
        return redirect(url_for("reports.index"))

    group_name = data["group"].name.replace(" ", "_")
    filename = f"reporte_grupo_{group_name}.pdf"
    output_path = os.path.join(EXPORTS_DIR, filename)

    pdf_svc = PDFService()
    pdf_svc.generate_group_report(data, output_path)

    return send_file(output_path, as_attachment=True, download_name=filename)
