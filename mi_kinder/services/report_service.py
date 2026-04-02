"""Servicio de agregacion de datos para reportes."""
import sqlite3
from mi_kinder.repositories.evaluation_repository import (
    EvaluationRepository, EvaluationAreaRepository, GradingScaleRepository,
)
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.school_year_repository import PeriodRepository
from mi_kinder.repositories.observation_repository import ObservationRepository


class ReportService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._eval_repo = EvaluationRepository(conn)
        self._area_repo = EvaluationAreaRepository(conn)
        self._scale_repo = GradingScaleRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._period_repo = PeriodRepository(conn)
        self._obs_repo = ObservationRepository(conn)

    def get_individual_report_data(self, student_id: int, school_year_id: int) -> dict:
        student = self._student_repo.get_by_id(student_id)
        if not student:
            return {}

        periods = self._period_repo.get_by_school_year(school_year_id)
        areas = self._area_repo.get_by_school_year(school_year_id)
        evaluations = self._eval_repo.get_for_student(student_id)
        observations = self._obs_repo.get_by_student(student_id)

        # Organizar evaluaciones en tabla: area x periodo
        eval_table = {}
        for e in evaluations:
            eval_table[(e.evaluation_area_id, e.period_id)] = e

        school_info = self._get_school_info()

        return {
            "student": student,
            "periods": periods,
            "areas": areas,
            "eval_table": eval_table,
            "observations": observations,
            "school_info": school_info,
        }

    def get_group_report_data(self, group_id: int, school_year_id: int) -> dict:
        group = self._group_repo.get_by_id(group_id)
        students = self._student_repo.get_by_group(group_id)
        periods = self._period_repo.get_by_school_year(school_year_id)
        areas = self._area_repo.get_by_school_year(school_year_id)

        # Para cada periodo, obtener promedios del grupo
        period_averages = {}
        for p in periods:
            avgs = self._eval_repo.get_group_averages(group_id, p.id)
            period_averages[p.id] = {a["area_id"]: a["avg_value"] for a in avgs}

        # Promedios por alumno
        student_averages = []
        for s in students:
            evals = self._eval_repo.get_for_student(s.id)
            if evals:
                avg = sum(e.numeric_value for e in evals if e.numeric_value) / max(
                    len([e for e in evals if e.numeric_value]), 1
                )
            else:
                avg = 0
            student_averages.append({"student": s, "average": avg})

        student_averages.sort(key=lambda x: x["average"], reverse=True)

        return {
            "group": group,
            "students": students,
            "periods": periods,
            "areas": areas,
            "period_averages": period_averages,
            "student_averages": student_averages,
            "school_info": self._get_school_info(),
        }

    def get_general_report_data(self, school_year_id: int) -> dict:
        groups = self._group_repo.get_all(school_year_id)
        periods = self._period_repo.get_by_school_year(school_year_id)
        areas = self._area_repo.get_by_school_year(school_year_id)

        # Promedios por grupo y area (ultimo periodo)
        group_data = []
        last_period = periods[-1] if periods else None
        for g in groups:
            if last_period:
                avgs = self._eval_repo.get_group_averages(g.id, last_period.id)
                avg_map = {a["area_name"]: a["avg_value"] for a in avgs}
            else:
                avg_map = {}
            group_data.append({"group": g, "averages": avg_map})

        return {
            "groups": groups,
            "periods": periods,
            "areas": areas,
            "group_data": group_data,
            "school_info": self._get_school_info(),
        }

    def _get_school_info(self) -> dict:
        row = self._conn.execute("SELECT * FROM school_info WHERE id = 1").fetchone()
        return dict(row) if row else {}
