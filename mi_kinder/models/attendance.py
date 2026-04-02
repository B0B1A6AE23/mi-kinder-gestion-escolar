"""Modelo de asistencia."""
from dataclasses import dataclass


@dataclass
class AttendanceRecord:
    id: int | None = None
    student_id: int = 0
    date: str = ""
    status: str = "present"  # present, absent, late, justified
    notes: str = ""
    recorded_by: int | None = None
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "AttendanceRecord":
        return AttendanceRecord(
            id=row["id"],
            student_id=row["student_id"],
            date=row["date"],
            status=row["status"],
            notes=row["notes"] or "",
            recorded_by=row["recorded_by"],
            created_at=row["created_at"],
        )
