"""Servicio de graficas con matplotlib."""
import sqlite3
import numpy as np
from mi_kinder.repositories.evaluation_repository import (
    EvaluationRepository, EvaluationAreaRepository, GradingScaleRepository,
)
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.school_year_repository import PeriodRepository


class ChartService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._eval_repo = EvaluationRepository(conn)
        self._area_repo = EvaluationAreaRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._period_repo = PeriodRepository(conn)
        self._scale_repo = GradingScaleRepository(conn)

    def get_student_progress_data(self, student_id: int, school_year_id: int) -> dict:
        """Datos para grafica de linea de progreso individual."""
        periods = self._period_repo.get_by_school_year(school_year_id)
        areas = self._area_repo.get_by_school_year(school_year_id)
        progress = self._eval_repo.get_student_progress(student_id)

        # Organizar: {area_name: [valor_p1, valor_p2, ...]}
        series = {}
        period_names = [p.name for p in periods]
        period_id_order = {p.id: i for i, p in enumerate(periods)}

        for a in areas:
            series[a.name] = [None] * len(periods)

        for row in progress:
            area_name = row["area_name"]
            period_name = row["period_name"]
            val = row["numeric_value"]
            if area_name in series and period_name in period_names:
                idx = period_names.index(period_name)
                series[area_name][idx] = val

        return {
            "period_names": period_names,
            "series": series,
            "student": self._student_repo.get_by_id(student_id),
        }

    def get_student_radar_data(self, student_id: int, period_id: int, school_year_id: int) -> dict:
        """Datos para grafica radar de un alumno en un periodo."""
        areas = self._area_repo.get_by_school_year(school_year_id)
        evals = self._eval_repo.get_for_student(student_id)

        labels = [a.name for a in areas]
        values = []
        for a in areas:
            ev = next((e for e in evals if e.evaluation_area_id == a.id and e.period_id == period_id), None)
            values.append(ev.numeric_value if ev and ev.numeric_value else 0)

        scale = self._scale_repo.get_default()
        max_val = max((l.numeric_value for l in (scale.levels or []) if l.numeric_value), default=3)

        return {"labels": labels, "values": values, "max_val": max_val}

    def get_group_bar_data(self, group_id: int, period_id: int) -> dict:
        """Datos para barras de promedio grupal por area."""
        avgs = self._eval_repo.get_group_averages(group_id, period_id)
        return {
            "area_names": [a["area_name"] for a in avgs],
            "averages": [a["avg_value"] or 0 for a in avgs],
        }

    def get_group_distribution_data(self, group_id: int, period_id: int, school_year_id: int) -> dict:
        """Datos para barra apilada de distribucion de niveles."""
        areas = self._area_repo.get_by_school_year(school_year_id)
        scale = self._scale_repo.get_default()
        levels = scale.levels if scale else []
        evals = self._eval_repo.get_for_group_period(group_id, period_id)

        data = {}
        for a in areas:
            data[a.name] = {l.label: 0 for l in levels}

        for e in evals:
            if e.area_name in data and e.grade_label in data[e.area_name]:
                data[e.area_name][e.grade_label] += 1

        return {
            "area_names": [a.name for a in areas],
            "level_labels": [l.label for l in levels],
            "level_colors": [l.color for l in levels],
            "data": data,
        }

    def get_general_comparison_data(self, school_year_id: int) -> dict:
        """Comparacion de promedios entre grupos por area."""
        groups = self._group_repo.get_all(school_year_id)
        areas = self._area_repo.get_by_school_year(school_year_id)
        periods = self._period_repo.get_by_school_year(school_year_id)
        last_period = periods[-1] if periods else None

        group_names = [g.name for g in groups]
        area_names = [a.name for a in areas]

        matrix = []
        for g in groups:
            row = []
            if last_period:
                avgs = self._eval_repo.get_group_averages(g.id, last_period.id)
                avg_map = {a["area_name"]: a["avg_value"] or 0 for a in avgs}
            else:
                avg_map = {}
            for a in areas:
                row.append(avg_map.get(a.name, 0))
            matrix.append(row)

        return {
            "group_names": group_names,
            "area_names": area_names,
            "matrix": matrix,
        }
