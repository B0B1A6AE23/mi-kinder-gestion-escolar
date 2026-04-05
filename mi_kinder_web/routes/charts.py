"""Rutas de graficas."""
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from mi_kinder_web.app import get_db

charts_bp = Blueprint("charts", __name__)


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@charts_bp.route("/charts")
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

    return render_template("charts.html", groups=groups, periods=periods)


@charts_bp.route("/charts/group-averages")
@login_required
def group_averages():
    db = get_db()
    group_id = request.args.get("group_id", type=int)
    period_id = request.args.get("period_id", type=int)

    if not group_id or not period_id:
        return jsonify({"error": "Faltan parametros"}), 400

    avgs = db.execute(
        """SELECT ea.name as area_name,
                  AVG(e.numeric_value) as avg_value,
                  COUNT(e.id) as eval_count
           FROM evaluation_areas ea
           LEFT JOIN evaluations e ON e.evaluation_area_id = ea.id AND e.period_id = ?
           LEFT JOIN students s ON s.id = e.student_id AND s.group_id = ?
           WHERE ea.school_year_id = (SELECT school_year_id FROM periods WHERE id = ?)
             AND ea.is_active = 1
           GROUP BY ea.id ORDER BY ea.sort_order""",
        (period_id, group_id, period_id),
    ).fetchall()

    if not avgs:
        return jsonify({"image": None, "message": "Sin datos"})

    area_names = [a["area_name"] for a in avgs]
    values = [a["avg_value"] or 0 for a in avgs]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#FFB74D", "#4FC3F7", "#81C784", "#E57373", "#BA68C8", "#FFD54F"]
    bars = ax.bar(area_names, values, color=[colors[i % len(colors)] for i in range(len(area_names))])

    ax.set_ylabel("Promedio")
    ax.set_title("Promedios por Área")
    ax.set_ylim(0, 3.5)
    ax.tick_params(axis="x", rotation=30)

    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    f"{val:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

    fig.tight_layout()
    img = fig_to_base64(fig)
    return jsonify({"image": img})


@charts_bp.route("/charts/group-distribution")
@login_required
def group_distribution():
    db = get_db()
    group_id = request.args.get("group_id", type=int)
    period_id = request.args.get("period_id", type=int)

    if not group_id or not period_id:
        return jsonify({"error": "Faltan parametros"}), 400

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1 ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    scale = db.execute(
        "SELECT * FROM grading_scales WHERE is_default = 1"
    ).fetchone()

    levels = []
    if scale:
        levels = db.execute(
            "SELECT * FROM grading_scale_levels WHERE grading_scale_id = ? ORDER BY sort_order",
            (scale["id"],),
        ).fetchall()

    evals = db.execute(
        """SELECT e.evaluation_area_id, gsl.label as grade_label, COUNT(*) as cnt
           FROM evaluations e
           JOIN students s ON s.id = e.student_id AND s.group_id = ?
           LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
           WHERE e.period_id = ?
           GROUP BY e.evaluation_area_id, gsl.label""",
        (group_id, period_id),
    ).fetchall()

    # Build data matrix
    area_names = [a["name"] for a in areas]
    area_id_map = {a["id"]: i for i, a in enumerate(areas)}
    level_labels = [l["label"] for l in levels]
    level_colors = [l["color"] for l in levels]

    data = {lbl: [0] * len(areas) for lbl in level_labels}
    for ev in evals:
        aid = ev["evaluation_area_id"]
        lbl = ev["grade_label"]
        if aid in area_id_map and lbl in data:
            data[lbl][area_id_map[aid]] = ev["cnt"]

    if not area_names:
        return jsonify({"image": None, "message": "Sin datos"})

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(area_names))
    width = 0.6
    bottom = np.zeros(len(area_names))

    for lbl, color in zip(level_labels, level_colors):
        vals = data.get(lbl, [0] * len(area_names))
        ax.bar(x, vals, width, label=lbl, bottom=bottom, color=color)
        bottom += np.array(vals)

    ax.set_xticks(x)
    ax.set_xticklabels(area_names, rotation=30, ha="right")
    ax.set_ylabel("Cantidad de alumnos")
    ax.set_title("Distribución de Niveles por Área")
    ax.legend()
    fig.tight_layout()

    img = fig_to_base64(fig)
    return jsonify({"image": img})


@charts_bp.route("/charts/student-progress")
@login_required
def student_progress():
    db = get_db()
    student_id = request.args.get("student_id", type=int)

    if not student_id:
        return jsonify({"error": "Falta student_id"}), 400

    active_year = db.execute(
        "SELECT * FROM school_years WHERE is_active = 1"
    ).fetchone()
    year_id = active_year["id"] if active_year else 0

    periods = db.execute(
        "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    areas = db.execute(
        "SELECT * FROM evaluation_areas WHERE school_year_id = ? AND is_active = 1 ORDER BY sort_order",
        (year_id,),
    ).fetchall()

    progress = db.execute(
        """SELECT ea.name as area_name, p.name as period_name,
                  p.sort_order as period_order, e.numeric_value
           FROM evaluations e
           JOIN evaluation_areas ea ON ea.id = e.evaluation_area_id
           JOIN periods p ON p.id = e.period_id
           WHERE e.student_id = ?
           ORDER BY ea.sort_order, p.sort_order""",
        (student_id,),
    ).fetchall()

    period_names = [p["name"] for p in periods]
    series = {}
    for a in areas:
        series[a["name"]] = [None] * len(periods)

    for row in progress:
        area_name = row["area_name"]
        period_name = row["period_name"]
        if area_name in series and period_name in period_names:
            idx = period_names.index(period_name)
            series[area_name][idx] = row["numeric_value"]

    if not period_names or not series:
        return jsonify({"image": None, "message": "Sin datos"})

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#FFB74D", "#4FC3F7", "#81C784", "#E57373", "#BA68C8", "#FFD54F"]

    for i, (area_name, values) in enumerate(series.items()):
        valid_x = [j for j, v in enumerate(values) if v is not None]
        valid_y = [v for v in values if v is not None]
        if valid_x:
            ax.plot(valid_x, valid_y, marker="o", label=area_name,
                    color=colors[i % len(colors)], linewidth=2)

    ax.set_xticks(range(len(period_names)))
    ax.set_xticklabels(period_names)
    ax.set_ylabel("Valor")
    ax.set_title("Progreso del Alumno")
    ax.set_ylim(0, 3.5)
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    img = fig_to_base64(fig)
    return jsonify({"image": img})


@charts_bp.route("/charts/attendance-chart")
@login_required
def attendance_chart():
    db = get_db()
    group_id = request.args.get("group_id", type=int)
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    if not group_id or not start_date or not end_date:
        return jsonify({"error": "Faltan parametros"}), 400

    data = db.execute(
        """SELECT ar.date,
                  COUNT(CASE WHEN ar.status='present' THEN 1 END) as present,
                  COUNT(CASE WHEN ar.status='absent' THEN 1 END) as absent,
                  COUNT(CASE WHEN ar.status='late' THEN 1 END) as late,
                  COUNT(*) as total
           FROM attendance_records ar
           JOIN students s ON s.id = ar.student_id
           WHERE s.group_id = ? AND ar.date BETWEEN ? AND ?
           GROUP BY ar.date ORDER BY ar.date""",
        (group_id, start_date, end_date),
    ).fetchall()

    if not data:
        return jsonify({"image": None, "message": "Sin datos de asistencia"})

    dates = [d["date"][5:] for d in data]
    present = [d["present"] for d in data]
    absent = [d["absent"] for d in data]
    late = [d["late"] for d in data]

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(dates))
    w = 0.25

    ax.bar(x - w, present, w, label="Presentes", color="#4CAF50")
    ax.bar(x, absent, w, label="Faltas", color="#F44336")
    ax.bar(x + w, late, w, label="Retardos", color="#FFC107")

    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("Alumnos")
    ax.set_title("Asistencia Diaria")
    ax.legend()
    fig.tight_layout()

    img = fig_to_base64(fig)
    return jsonify({"image": img})
