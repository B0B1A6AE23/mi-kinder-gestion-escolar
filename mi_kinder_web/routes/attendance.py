"""Rutas de asistencia."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import date

from mi_kinder_web.app import get_db

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/attendance")
@login_required
def index():
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    selected_group = request.args.get("group_id", type=int)
    selected_date = request.args.get("date", date.today().isoformat())

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    students = []
    attendance_map = {}

    if selected_group:
        students = db.execute(
            """SELECT s.id, s.first_name, s.last_name, s.second_last_name,
                      s.photo_path, s.discapacidad, s.aptitud_sobresaliente, s.condicion_adicional
               FROM students s
               WHERE s.group_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name""",
            (selected_group,),
        ).fetchall()

        records = db.execute(
            """SELECT ar.student_id, ar.status, ar.notes
               FROM attendance_records ar
               JOIN students s ON s.id = ar.student_id
               WHERE s.group_id = ? AND ar.date = ?""",
            (selected_group, selected_date),
        ).fetchall()

        for r in records:
            attendance_map[r["student_id"]] = {
                "status": r["status"],
                "notes": r["notes"] or "",
            }

    return render_template(
        "attendance.html",
        groups=groups,
        students=students,
        attendance_map=attendance_map,
        selected_group=selected_group,
        selected_date=selected_date,
    )


@attendance_bp.route("/attendance/save", methods=["POST"])
@login_required
def save():
    db = get_db()
    group_id = request.form.get("group_id", type=int)
    att_date = request.form.get("date", date.today().isoformat())

    if not group_id:
        flash("Selecciona un grupo.", "error")
        return redirect(url_for("attendance.index"))

    students = db.execute(
        "SELECT id FROM students WHERE group_id = ? AND is_active = 1",
        (group_id,),
    ).fetchall()

    count = 0
    for student in students:
        sid = student["id"]
        status = request.form.get(f"status_{sid}", "present")
        notes = request.form.get(f"notes_{sid}", "").strip()

        existing = db.execute(
            "SELECT id FROM attendance_records WHERE student_id = ? AND date = ?",
            (sid, att_date),
        ).fetchone()

        if existing:
            db.execute(
                "UPDATE attendance_records SET status=?, notes=?, recorded_by=? WHERE id=?",
                (status, notes or None, current_user.id, existing["id"]),
            )
        else:
            db.execute(
                """INSERT INTO attendance_records (student_id, date, status, notes, recorded_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (sid, att_date, status, notes or None, current_user.id),
            )
        count += 1

    db.commit()
    flash(f"Asistencia guardada para {count} alumnos.", "success")
    return redirect(
        url_for("attendance.index", group_id=group_id, date=att_date)
    )


@attendance_bp.route("/attendance/report")
@login_required
def report():
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    group_id = request.args.get("group_id", type=int)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    report_data = []
    if group_id and start_date and end_date:
        students = db.execute(
            """SELECT s.id, s.first_name || ' ' || s.last_name as full_name
               FROM students s
               WHERE s.group_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name""",
            (group_id,),
        ).fetchall()

        for student in students:
            row = db.execute(
                """SELECT
                     COUNT(CASE WHEN status='present' THEN 1 END) as present,
                     COUNT(CASE WHEN status='absent' THEN 1 END) as absent,
                     COUNT(CASE WHEN status='late' THEN 1 END) as late,
                     COUNT(CASE WHEN status='justified' THEN 1 END) as justified,
                     COUNT(*) as total
                   FROM attendance_records
                   WHERE student_id = ? AND date BETWEEN ? AND ?""",
                (student["id"], start_date, end_date),
            ).fetchone()
            report_data.append({
                "name": student["full_name"],
                "present": row["present"],
                "absent": row["absent"],
                "late": row["late"],
                "justified": row["justified"],
                "total": row["total"],
                "rate": round(row["present"] * 100 / max(row["total"], 1), 1),
            })

    return render_template(
        "attendance_report.html",
        groups=groups,
        report_data=report_data,
        selected_group=group_id,
        start_date=start_date,
        end_date=end_date,
    )
