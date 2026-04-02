"""Modelos del sistema de evaluacion."""
from dataclasses import dataclass


@dataclass
class GradingScale:
    id: int | None = None
    name: str = ""
    scale_type: str = "label"  # numeric, letter, label
    school_year_id: int | None = None
    is_default: bool = False
    created_at: str = ""
    levels: list["GradingScaleLevel"] | None = None

    @staticmethod
    def from_row(row) -> "GradingScale":
        return GradingScale(
            id=row["id"],
            name=row["name"],
            scale_type=row["scale_type"],
            school_year_id=row["school_year_id"],
            is_default=bool(row["is_default"]),
            created_at=row["created_at"],
        )


@dataclass
class GradingScaleLevel:
    id: int | None = None
    grading_scale_id: int = 0
    label: str = ""
    numeric_value: float | None = None
    color: str = ""
    sort_order: int = 0

    @staticmethod
    def from_row(row) -> "GradingScaleLevel":
        return GradingScaleLevel(
            id=row["id"],
            grading_scale_id=row["grading_scale_id"],
            label=row["label"],
            numeric_value=row["numeric_value"],
            color=row["color"] or "",
            sort_order=row["sort_order"],
        )


@dataclass
class EvaluationArea:
    id: int | None = None
    school_year_id: int = 0
    name: str = ""
    description: str = ""
    sort_order: int = 0
    is_active: bool = True
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "EvaluationArea":
        return EvaluationArea(
            id=row["id"],
            school_year_id=row["school_year_id"],
            name=row["name"],
            description=row["description"] or "",
            sort_order=row["sort_order"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )


@dataclass
class Evaluation:
    id: int | None = None
    student_id: int = 0
    evaluation_area_id: int = 0
    period_id: int = 0
    grading_scale_id: int = 0
    grade_level_id: int | None = None
    numeric_value: float | None = None
    observations: str = ""
    evaluated_by: int | None = None
    evaluated_at: str = ""
    created_at: str = ""
    updated_at: str = ""
    # Campos de JOINs
    area_name: str = ""
    period_name: str = ""
    grade_label: str = ""
    grade_color: str = ""
    student_name: str = ""

    @staticmethod
    def from_row(row) -> "Evaluation":
        e = Evaluation(
            id=row["id"],
            student_id=row["student_id"],
            evaluation_area_id=row["evaluation_area_id"],
            period_id=row["period_id"],
            grading_scale_id=row["grading_scale_id"],
            grade_level_id=row["grade_level_id"],
            numeric_value=row["numeric_value"],
            observations=row["observations"] or "",
            evaluated_by=row["evaluated_by"],
            evaluated_at=row["evaluated_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        keys = row.keys()
        if "area_name" in keys:
            e.area_name = row["area_name"] or ""
        if "period_name" in keys:
            e.period_name = row["period_name"] or ""
        if "grade_label" in keys:
            e.grade_label = row["grade_label"] or ""
        if "grade_color" in keys:
            e.grade_color = row["grade_color"] or ""
        if "student_name" in keys:
            e.student_name = row["student_name"] or ""
        return e
