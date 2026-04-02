"""Modelo de observaciones de alumnos."""
from dataclasses import dataclass


@dataclass
class StudentObservation:
    id: int | None = None
    student_id: int = 0
    period_id: int | None = None
    content: str = ""
    category: str = "general"
    created_by: int | None = None
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "StudentObservation":
        return StudentObservation(
            id=row["id"],
            student_id=row["student_id"],
            period_id=row["period_id"],
            content=row["content"],
            category=row["category"] or "general",
            created_by=row["created_by"],
            created_at=row["created_at"],
        )
