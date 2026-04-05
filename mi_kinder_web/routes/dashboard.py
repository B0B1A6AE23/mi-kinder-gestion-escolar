"""Rutas del dashboard principal."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, timedelta

from mi_kinder_web.app import get_db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    db = get_db()
    today = date.today().isoformat()
    thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()

    # Active school year
    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()

    year_id = active_year["id"] if active_year else 0

    # Basic stats
    total_students = db.execute(
        """SELECT COUNT(*) c FROM students s
           JOIN groups_ g ON g.id = s.group_id
           WHERE g.school_year_id = ? AND s.is_active = 1""",
        (year_id,),
    ).fetchone()["c"]

    total_groups = db.execute(
        "SELECT COUNT(*) c FROM groups_ WHERE school_year_id = ? AND is_active = 1",
        (year_id,),
    ).fetchone()["c"]

    total_teachers = db.execute(
        "SELECT COUNT(*) c FROM users WHERE role = 'maestra' AND is_active = 1"
    ).fetchone()["c"]

    # Attendance rate last 30 days
    att_row = db.execute(
        """SELECT
             COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0
             / NULLIF(COUNT(*), 0) as rate
           FROM attendance_records ar
           JOIN students s ON s.id = ar.student_id
           JOIN groups_ g ON g.id = s.group_id
           WHERE g.school_year_id = ? AND ar.date BETWEEN ? AND ?""",
        (year_id, thirty_days_ago, today),
    ).fetchone()
    attendance_rate = round(att_row["rate"], 1) if att_row and att_row["rate"] else 0

    stats = {
        "students": total_students,
        "groups": total_groups,
        "teachers": total_teachers,
        "attendance_rate": attendance_rate,
    }

    # Groups summary
    groups = db.execute(
        """SELECT g.id, g.name, g.grade_level,
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

    # Recent absences (last 7 days)
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    absences = db.execute(
        """SELECT s.first_name || ' ' || s.last_name as student_name,
                  g.name as group_name, ar.date, ar.status
           FROM attendance_records ar
           JOIN students s ON s.id = ar.student_id
           JOIN groups_ g ON g.id = s.group_id
           WHERE ar.status IN ('absent', 'late')
             AND ar.date BETWEEN ? AND ?
             AND g.school_year_id = ?
           ORDER BY ar.date DESC LIMIT 15""",
        (seven_days_ago, today, year_id),
    ).fetchall()

    # Upcoming birthdays — only next 30 days, never past birthdays
    next_30 = (date.today() + timedelta(days=30))
    today_mmdd = date.today().strftime('%m-%d')
    next_mmdd  = next_30.strftime('%m-%d')
    no_rollover = today_mmdd <= next_mmdd

    if no_rollover:
        birthdays = db.execute(
            """SELECT s.id, s.first_name, s.last_name, s.second_last_name,
                      s.photo_path, s.discapacidad, s.aptitud_sobresaliente,
                      s.condicion_adicional, s.birth_date, g.name as group_name
               FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE g.school_year_id = ? AND s.is_active = 1
                 AND s.birth_date IS NOT NULL
                 AND strftime('%m-%d', s.birth_date) BETWEEN ? AND ?
               ORDER BY strftime('%m-%d', s.birth_date)
               LIMIT 5""",
            (year_id, today_mmdd, next_mmdd),
        ).fetchall()
    else:
        # Year-end rollover (e.g., Dec 20 → Jan 19)
        birthdays = db.execute(
            """SELECT s.id, s.first_name, s.last_name, s.second_last_name,
                      s.photo_path, s.discapacidad, s.aptitud_sobresaliente,
                      s.condicion_adicional, s.birth_date, g.name as group_name
               FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE g.school_year_id = ? AND s.is_active = 1
                 AND s.birth_date IS NOT NULL
                 AND (strftime('%m-%d', s.birth_date) >= ?
                      OR  strftime('%m-%d', s.birth_date) <= ?)
               ORDER BY
                 CASE WHEN strftime('%m-%d', s.birth_date) >= ? THEN 0 ELSE 1 END,
                 strftime('%m-%d', s.birth_date)
               LIMIT 5""",
            (year_id, today_mmdd, next_mmdd, today_mmdd),
        ).fetchall()

    return render_template(
        "dashboard.html",
        stats=stats,
        groups=groups,
        absences=absences,
        birthdays=birthdays,
        today_iso=today,
    )
