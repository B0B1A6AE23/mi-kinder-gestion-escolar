"""Repositorio de evaluaciones, escalas y areas."""
import sqlite3
from mi_kinder.models.evaluation import (
    Evaluation, EvaluationArea, GradingScale, GradingScaleLevel,
)
from mi_kinder.repositories.base_repository import BaseRepository


class GradingScaleRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "grading_scales")

    def get_all(self, school_year_id: int | None = None) -> list[GradingScale]:
        if school_year_id:
            rows = self._fetch_all(
                "SELECT * FROM grading_scales WHERE school_year_id = ? OR school_year_id IS NULL ORDER BY name",
                (school_year_id,),
            )
        else:
            rows = self._fetch_all("SELECT * FROM grading_scales ORDER BY name")
        scales = []
        for r in rows:
            scale = GradingScale.from_row(r)
            scale.levels = self.get_levels(scale.id)
            scales.append(scale)
        return scales

    def get_default(self) -> GradingScale | None:
        row = self._fetch_one("SELECT * FROM grading_scales WHERE is_default = 1")
        if not row:
            return None
        scale = GradingScale.from_row(row)
        scale.levels = self.get_levels(scale.id)
        return scale

    def get_by_id(self, scale_id: int) -> GradingScale | None:
        row = self._fetch_one("SELECT * FROM grading_scales WHERE id = ?", (scale_id,))
        if not row:
            return None
        scale = GradingScale.from_row(row)
        scale.levels = self.get_levels(scale.id)
        return scale

    def get_levels(self, scale_id: int) -> list[GradingScaleLevel]:
        rows = self._fetch_all(
            "SELECT * FROM grading_scale_levels WHERE grading_scale_id = ? ORDER BY sort_order",
            (scale_id,),
        )
        return [GradingScaleLevel.from_row(r) for r in rows]

    def create(self, scale: GradingScale, levels: list[GradingScaleLevel]) -> int:
        cursor = self._execute(
            """INSERT INTO grading_scales (name, scale_type, school_year_id, is_default)
               VALUES (?, ?, ?, ?)""",
            (scale.name, scale.scale_type, scale.school_year_id, int(scale.is_default)),
        )
        scale_id = cursor.lastrowid
        for level in levels:
            self._execute(
                """INSERT INTO grading_scale_levels
                   (grading_scale_id, label, numeric_value, color, sort_order)
                   VALUES (?, ?, ?, ?, ?)""",
                (scale_id, level.label, level.numeric_value, level.color, level.sort_order),
            )
        self.conn.commit()
        return scale_id


class EvaluationAreaRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "evaluation_areas")

    def get_by_school_year(self, school_year_id: int, active_only: bool = True) -> list[EvaluationArea]:
        sql = "SELECT * FROM evaluation_areas WHERE school_year_id = ?"
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY sort_order"
        return [EvaluationArea.from_row(r) for r in self._fetch_all(sql, (school_year_id,))]

    def create(self, area: EvaluationArea) -> int:
        cursor = self._execute(
            """INSERT INTO evaluation_areas (school_year_id, name, description, sort_order, is_active)
               VALUES (?, ?, ?, ?, ?)""",
            (area.school_year_id, area.name, area.description or None,
             area.sort_order, int(area.is_active)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update(self, area: EvaluationArea):
        self._execute(
            """UPDATE evaluation_areas SET name=?, description=?, sort_order=?, is_active=?
               WHERE id=?""",
            (area.name, area.description or None, area.sort_order, int(area.is_active), area.id),
        )
        self.conn.commit()


class EvaluationRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "evaluations")

    def get_for_student(self, student_id: int) -> list[Evaluation]:
        rows = self._fetch_all(
            """SELECT e.*, ea.name as area_name, p.name as period_name,
                      gsl.label as grade_label, gsl.color as grade_color
               FROM evaluations e
               JOIN evaluation_areas ea ON ea.id = e.evaluation_area_id
               JOIN periods p ON p.id = e.period_id
               LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
               WHERE e.student_id = ?
               ORDER BY p.sort_order, ea.sort_order""",
            (student_id,),
        )
        return [Evaluation.from_row(r) for r in rows]

    def get_for_group_period(self, group_id: int, period_id: int) -> list[Evaluation]:
        rows = self._fetch_all(
            """SELECT e.*, ea.name as area_name, p.name as period_name,
                      gsl.label as grade_label, gsl.color as grade_color,
                      s.first_name || ' ' || s.last_name as student_name
               FROM evaluations e
               JOIN students s ON s.id = e.student_id
               JOIN evaluation_areas ea ON ea.id = e.evaluation_area_id
               JOIN periods p ON p.id = e.period_id
               LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
               WHERE s.group_id = ? AND e.period_id = ?
               ORDER BY s.last_name, s.first_name, ea.sort_order""",
            (group_id, period_id),
        )
        return [Evaluation.from_row(r) for r in rows]

    def upsert(self, evaluation: Evaluation) -> int:
        existing = self._fetch_one(
            """SELECT id FROM evaluations
               WHERE student_id=? AND evaluation_area_id=? AND period_id=?""",
            (evaluation.student_id, evaluation.evaluation_area_id, evaluation.period_id),
        )
        if existing:
            self._execute(
                """UPDATE evaluations SET grading_scale_id=?, grade_level_id=?,
                   numeric_value=?, observations=?, evaluated_by=?,
                   evaluated_at=datetime('now'), updated_at=datetime('now')
                   WHERE id=?""",
                (evaluation.grading_scale_id, evaluation.grade_level_id,
                 evaluation.numeric_value, evaluation.observations or None,
                 evaluation.evaluated_by, existing["id"]),
            )
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self._execute(
                """INSERT INTO evaluations (student_id, evaluation_area_id, period_id,
                   grading_scale_id, grade_level_id, numeric_value, observations, evaluated_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (evaluation.student_id, evaluation.evaluation_area_id, evaluation.period_id,
                 evaluation.grading_scale_id, evaluation.grade_level_id,
                 evaluation.numeric_value, evaluation.observations or None,
                 evaluation.evaluated_by),
            )
            self.conn.commit()
            return cursor.lastrowid

    def get_group_averages(self, group_id: int, period_id: int) -> list[dict]:
        rows = self._fetch_all(
            """SELECT ea.name as area_name, ea.id as area_id,
                      AVG(e.numeric_value) as avg_value,
                      COUNT(e.id) as eval_count
               FROM evaluation_areas ea
               LEFT JOIN evaluations e ON e.evaluation_area_id = ea.id AND e.period_id = ?
               LEFT JOIN students s ON s.id = e.student_id AND s.group_id = ?
               WHERE ea.school_year_id = (SELECT school_year_id FROM periods WHERE id = ?)
               AND ea.is_active = 1
               GROUP BY ea.id ORDER BY ea.sort_order""",
            (period_id, group_id, period_id),
        )
        return [dict(r) for r in rows]

    def get_student_progress(self, student_id: int) -> list[dict]:
        rows = self._fetch_all(
            """SELECT ea.name as area_name, p.name as period_name,
                      p.sort_order as period_order, e.numeric_value,
                      gsl.label as grade_label
               FROM evaluations e
               JOIN evaluation_areas ea ON ea.id = e.evaluation_area_id
               JOIN periods p ON p.id = e.period_id
               LEFT JOIN grading_scale_levels gsl ON gsl.id = e.grade_level_id
               WHERE e.student_id = ?
               ORDER BY ea.sort_order, p.sort_order""",
            (student_id,),
        )
        return [dict(r) for r in rows]
