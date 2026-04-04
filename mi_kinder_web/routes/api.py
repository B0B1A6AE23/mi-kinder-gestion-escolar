"""API routes for AJAX calls."""
from flask import Blueprint, request, jsonify
from flask_login import login_required

from mi_kinder_web.app import get_db

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/students-list")
@login_required
def students_list():
    """Return a JSON list of students for a given group."""
    db = get_db()
    group_id = request.args.get("group_id", type=int)
    if not group_id:
        return jsonify([])

    students = db.execute(
        """SELECT s.id, s.first_name || ' ' || s.last_name || ' ' || COALESCE(s.second_last_name, '') as name
           FROM students s
           WHERE s.group_id = ? AND s.is_active = 1
           ORDER BY s.last_name, s.first_name""",
        (group_id,),
    ).fetchall()

    return jsonify([{"id": s["id"], "name": s["name"].strip()} for s in students])
