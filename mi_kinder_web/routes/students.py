"""Rutas de gestion de alumnos."""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import date

from mi_kinder_web.app import get_db
from mi_kinder_web.config import PHOTOS_DIR

students_bp = Blueprint("students", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@students_bp.route("/students")
@login_required
def index():
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    group_id = request.args.get("group_id", type=int)
    search_q = request.args.get("q", "").strip()

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    if search_q:
        pattern = f"%{search_q}%"
        students = db.execute(
            """SELECT s.*, g.name as group_name
               FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE g.school_year_id = ? AND s.is_active = 1
                 AND (s.first_name LIKE ? OR s.last_name LIKE ?
                      OR s.second_last_name LIKE ? OR s.curp LIKE ?)
               ORDER BY s.last_name, s.first_name LIMIT 100""",
            (year_id, pattern, pattern, pattern, pattern),
        ).fetchall()
    elif group_id:
        students = db.execute(
            """SELECT s.*, g.name as group_name
               FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE s.group_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name""",
            (group_id,),
        ).fetchall()
    else:
        students = db.execute(
            """SELECT s.*, g.name as group_name
               FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE g.school_year_id = ? AND s.is_active = 1
               ORDER BY s.last_name, s.first_name LIMIT 200""",
            (year_id,),
        ).fetchall()

    return render_template(
        "students.html",
        students=students,
        groups=groups,
        selected_group=group_id,
        search_q=search_q,
    )


@students_bp.route("/students/<int:student_id>")
@login_required
def detail(student_id):
    db = get_db()
    student = db.execute(
        """SELECT s.*, g.name as group_name
           FROM students s
           JOIN groups_ g ON g.id = s.group_id
           WHERE s.id = ?""",
        (student_id,),
    ).fetchone()

    if not student:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("students.index"))

    # Attendance summary
    attendance = db.execute(
        """SELECT status, COUNT(*) as cnt
           FROM attendance_records
           WHERE student_id = ?
           GROUP BY status""",
        (student_id,),
    ).fetchall()
    att_summary = {row["status"]: row["cnt"] for row in attendance}

    # Evaluations
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

    # Observations
    observations = db.execute(
        """SELECT so.*, u.full_name as author_name
           FROM student_observations so
           LEFT JOIN users u ON u.id = so.created_by
           WHERE so.student_id = ?
           ORDER BY so.created_at DESC LIMIT 20""",
        (student_id,),
    ).fetchall()

    return render_template(
        "student_detail.html",
        student=student,
        att_summary=att_summary,
        evaluations=evaluations,
        observations=observations,
    )


@students_bp.route("/students/create", methods=["GET", "POST"])
@login_required
def create():
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
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        second_last_name = request.form.get("second_last_name", "").strip()
        group_id = request.form.get("group_id", type=int)
        curp = request.form.get("curp", "").strip().upper()
        birth_date = request.form.get("birth_date", "")
        gender = request.form.get("gender", "")
        guardian_name = request.form.get("guardian_name", "").strip()
        guardian_phone = request.form.get("guardian_phone", "").strip()
        guardian_email = request.form.get("guardian_email", "").strip()
        address = request.form.get("address", "").strip()
        blood_type = request.form.get("blood_type", "").strip()
        allergies = request.form.get("allergies", "").strip()
        medical_notes = request.form.get("medical_notes", "").strip()

        if not first_name or not last_name or not group_id:
            flash("Nombre, apellido y grupo son obligatorios.", "error")
            return render_template("student_form.html", student=None, groups=groups)

        # Handle photo upload
        photo_path = None
        if "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename and allowed_file(photo.filename):
                ext = photo.filename.rsplit(".", 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                photo.save(os.path.join(PHOTOS_DIR, filename))
                photo_path = filename

        db.execute(
            """INSERT INTO students (group_id, first_name, last_name, second_last_name,
               curp, birth_date, gender, photo_path, enrollment_date,
               guardian_name, guardian_phone, guardian_email, address,
               blood_type, allergies, medical_notes, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                group_id, first_name, last_name,
                second_last_name or None, curp or None,
                birth_date or None, gender or None, photo_path,
                date.today().isoformat(),
                guardian_name or None, guardian_phone or None,
                guardian_email or None, address or None,
                blood_type or None, allergies or None,
                medical_notes or None,
            ),
        )
        db.commit()

        flash(f"Alumno '{first_name} {last_name}' registrado.", "success")
        return redirect(url_for("students.index"))

    return render_template("student_form.html", student=None, groups=groups)


@students_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit(student_id):
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if not student:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("students.index"))

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    groups = db.execute(
        "SELECT * FROM groups_ WHERE school_year_id = ? AND is_active = 1 ORDER BY name",
        (year_id,),
    ).fetchall()

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        second_last_name = request.form.get("second_last_name", "").strip()
        group_id = request.form.get("group_id", type=int)
        curp = request.form.get("curp", "").strip().upper()
        birth_date = request.form.get("birth_date", "")
        gender = request.form.get("gender", "")
        guardian_name = request.form.get("guardian_name", "").strip()
        guardian_phone = request.form.get("guardian_phone", "").strip()
        guardian_email = request.form.get("guardian_email", "").strip()
        address = request.form.get("address", "").strip()
        blood_type = request.form.get("blood_type", "").strip()
        allergies = request.form.get("allergies", "").strip()
        medical_notes = request.form.get("medical_notes", "").strip()

        if not first_name or not last_name or not group_id:
            flash("Nombre, apellido y grupo son obligatorios.", "error")
            return render_template("student_form.html", student=student, groups=groups)

        # Handle photo upload
        photo_path = student["photo_path"]
        if "photo" in request.files:
            photo = request.files["photo"]
            if photo.filename and allowed_file(photo.filename):
                ext = photo.filename.rsplit(".", 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                photo.save(os.path.join(PHOTOS_DIR, filename))
                photo_path = filename

        db.execute(
            """UPDATE students SET group_id=?, first_name=?, last_name=?,
               second_last_name=?, curp=?, birth_date=?, gender=?, photo_path=?,
               guardian_name=?, guardian_phone=?, guardian_email=?, address=?,
               blood_type=?, allergies=?, medical_notes=?,
               updated_at=datetime('now') WHERE id=?""",
            (
                group_id, first_name, last_name,
                second_last_name or None, curp or None,
                birth_date or None, gender or None, photo_path,
                guardian_name or None, guardian_phone or None,
                guardian_email or None, address or None,
                blood_type or None, allergies or None,
                medical_notes or None, student_id,
            ),
        )
        db.commit()

        flash(f"Alumno '{first_name} {last_name}' actualizado.", "success")
        return redirect(url_for("students.detail", student_id=student_id))

    return render_template("student_form.html", student=student, groups=groups)


@students_bp.route("/students/<int:student_id>/toggle", methods=["POST"])
@login_required
def toggle_active(student_id):
    if current_user.role != "directora":
        flash("Solo la directora puede dar de baja alumnos.", "error")
        return redirect(url_for("students.index"))

    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    if not student:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("students.index"))

    new_status = 0 if student["is_active"] else 1
    db.execute(
        "UPDATE students SET is_active=?, updated_at=datetime('now') WHERE id=?",
        (new_status, student_id),
    )
    db.commit()

    action = "activado" if new_status else "dado de baja"
    flash(f"Alumno {action} exitosamente.", "success")
    return redirect(url_for("students.detail", student_id=student_id))


@students_bp.route("/students/<int:student_id>/transfer", methods=["POST"])
@login_required
def transfer(student_id):
    db = get_db()
    student = db.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    if not student:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("students.index"))

    to_group_id = request.form.get("to_group_id", type=int)
    reason = request.form.get("reason", "").strip()

    if not to_group_id:
        flash("Selecciona un grupo destino.", "error")
        return redirect(url_for("students.detail", student_id=student_id))

    from_group_id = student["group_id"]
    db.execute(
        "UPDATE students SET group_id=?, updated_at=datetime('now') WHERE id=?",
        (to_group_id, student_id),
    )
    db.execute(
        """INSERT INTO student_transfers (student_id, from_group_id, to_group_id, reason, transferred_by)
           VALUES (?, ?, ?, ?, ?)""",
        (student_id, from_group_id, to_group_id, reason or None, current_user.id),
    )
    db.commit()

    flash("Alumno transferido exitosamente.", "success")
    return redirect(url_for("students.detail", student_id=student_id))
