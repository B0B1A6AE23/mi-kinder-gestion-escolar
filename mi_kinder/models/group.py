"""Modelo de grupo escolar."""
from dataclasses import dataclass


@dataclass
class Group:
    id: int | None = None
    school_year_id: int = 0
    name: str = ""
    grade_level: str = ""
    capacity: int | None = None
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    # Campos calculados (no en DB)
    teacher_name: str = ""
    student_count: int = 0

    @staticmethod
    def from_row(row) -> "Group":
        g = Group(
            id=row["id"],
            school_year_id=row["school_year_id"],
            name=row["name"],
            grade_level=row["grade_level"] or "",
            capacity=row["capacity"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        # Campos opcionales de JOINs
        keys = row.keys()
        if "teacher_name" in keys:
            g.teacher_name = row["teacher_name"] or ""
        if "student_count" in keys:
            g.student_count = row["student_count"] or 0
        return g
