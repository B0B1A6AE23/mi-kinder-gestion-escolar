"""Modelos de ciclo escolar y periodos."""
from dataclasses import dataclass


@dataclass
class SchoolYear:
    id: int | None = None
    name: str = ""
    start_date: str = ""
    end_date: str = ""
    is_active: bool = False
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "SchoolYear":
        return SchoolYear(
            id=row["id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )


@dataclass
class Period:
    id: int | None = None
    school_year_id: int = 0
    name: str = ""
    start_date: str = ""
    end_date: str = ""
    sort_order: int = 0
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "Period":
        return Period(
            id=row["id"],
            school_year_id=row["school_year_id"],
            name=row["name"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            sort_order=row["sort_order"],
            created_at=row["created_at"],
        )
