"""Rutas de gestion de grupos."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from mi_kinder_web.app import get_db

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups")
@login_required
def index():
    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    groups = db.execute(
        """SELECT g.id, g.name, g.grade_level, g.capacity,
                  u.full_name as teacher_name,
                  COUNT(DISTINCT s.id) as student_count
           FROM groups_ g
           LEFT JOIN user_group_assignments uga ON uga.group_id = g.id
           LEFT JOIN users u ON u.id = uga.user_id
           LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
           WHERE g.school_year_id = ? AND g.is_active = 1
           GROUP BY g.id ORDER BY g.name""",
        (year_id,),
    ).fetchall()

    return render_template("groups.html", groups=groups)


@groups_bp.route("/groups/<int:group_id>")
@login_required
def detail(group_id):
    db = get_db()
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
        return redirect(url_for("groups.index"))

    students = db.execute(
        """SELECT s.*, g.name as group_name
           FROM students s
           JOIN groups_ g ON g.id = s.group_id
           WHERE s.group_id = ? AND s.is_active = 1
           ORDER BY s.last_name, s.first_name""",
        (group_id,),
    ).fetchall()

    return render_template("group_detail.html", group=group, students=students)


@groups_bp.route("/groups/create", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "directora":
        flash("Solo la directora puede crear grupos.", "error")
        return redirect(url_for("groups.index"))

    db = get_db()
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        grade_level = request.form.get("grade_level", "").strip()
        capacity = request.form.get("capacity", "")
        teacher_id = request.form.get("teacher_id", "")

        if not name:
            flash("El nombre del grupo es obligatorio.", "error")
            return redirect(url_for("groups.create"))

        year_id = active_year["id"] if active_year else 0
        db.execute(
            """INSERT INTO groups_ (school_year_id, name, grade_level, capacity, is_active)
               VALUES (?, ?, ?, ?, 1)""",
            (year_id, name, grade_level or None, int(capacity) if capacity else None),
        )
        db.commit()

        if teacher_id:
            group_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute(
                "INSERT OR IGNORE INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
                (int(teacher_id), group_id),
            )
            db.commit()

        flash(f"Grupo '{name}' creado exitosamente.", "success")
        return redirect(url_for("groups.index"))

    teachers = db.execute(
        "SELECT * FROM users WHERE role = 'maestra' AND is_active = 1 ORDER BY full_name"
    ).fetchall()

    return render_template("group_form.html", group=None, teachers=teachers)


@groups_bp.route("/groups/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def edit(group_id):
    if current_user.role != "directora":
        flash("Solo la directora puede editar grupos.", "error")
        return redirect(url_for("groups.index"))

    db = get_db()
    group = db.execute("SELECT * FROM groups_ WHERE id = ?", (group_id,)).fetchone()
    if not group:
        flash("Grupo no encontrado.", "error")
        return redirect(url_for("groups.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        grade_level = request.form.get("grade_level", "").strip()
        capacity = request.form.get("capacity", "")
        teacher_id = request.form.get("teacher_id", "")

        if not name:
            flash("El nombre del grupo es obligatorio.", "error")
            return redirect(url_for("groups.edit", group_id=group_id))

        db.execute(
            """UPDATE groups_ SET name=?, grade_level=?, capacity=?,
               updated_at=datetime('now') WHERE id=?""",
            (name, grade_level or None, int(capacity) if capacity else None, group_id),
        )

        # Update teacher assignment
        db.execute(
            "DELETE FROM user_group_assignments WHERE group_id = ?", (group_id,)
        )
        if teacher_id:
            db.execute(
                "INSERT INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
                (int(teacher_id), group_id),
            )
        db.commit()

        flash(f"Grupo '{name}' actualizado.", "success")
        return redirect(url_for("groups.detail", group_id=group_id))

    teachers = db.execute(
        "SELECT * FROM users WHERE role = 'maestra' AND is_active = 1 ORDER BY full_name"
    ).fetchall()

    current_teacher = db.execute(
        "SELECT user_id FROM user_group_assignments WHERE group_id = ?",
        (group_id,),
    ).fetchone()
    current_teacher_id = current_teacher["user_id"] if current_teacher else None

    return render_template(
        "group_form.html",
        group=group,
        teachers=teachers,
        current_teacher_id=current_teacher_id,
    )
