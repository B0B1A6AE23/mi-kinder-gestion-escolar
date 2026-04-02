"""Repositorio de ciclos escolares y periodos."""
import sqlite3
from mi_kinder.models.school_year import SchoolYear, Period
from mi_kinder.repositories.base_repository import BaseRepository


class SchoolYearRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "school_years")

    def get_all(self) -> list[SchoolYear]:
        rows = self._fetch_all("SELECT * FROM school_years ORDER BY start_date DESC")
        return [SchoolYear.from_row(r) for r in rows]

    def get_active(self) -> SchoolYear | None:
        row = self._fetch_one("SELECT * FROM school_years WHERE is_active = 1")
        return SchoolYear.from_row(row) if row else None

    def get_by_id(self, year_id: int) -> SchoolYear | None:
        row = self._fetch_one("SELECT * FROM school_years WHERE id = ?", (year_id,))
        return SchoolYear.from_row(row) if row else None

    def create(self, year: SchoolYear) -> int:
        cursor = self._execute(
            """INSERT INTO school_years (name, start_date, end_date, is_active)
               VALUES (?, ?, ?, ?)""",
            (year.name, year.start_date, year.end_date, int(year.is_active)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def set_active(self, year_id: int):
        self._execute("UPDATE school_years SET is_active = 0")
        self._execute("UPDATE school_years SET is_active = 1 WHERE id = ?", (year_id,))
        self._execute("UPDATE school_info SET current_year_id = ? WHERE id = 1", (year_id,))
        self.conn.commit()

    def update(self, year: SchoolYear):
        self._execute(
            """UPDATE school_years SET name=?, start_date=?, end_date=? WHERE id=?""",
            (year.name, year.start_date, year.end_date, year.id),
        )
        self.conn.commit()


class PeriodRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "periods")

    def get_by_school_year(self, school_year_id: int) -> list[Period]:
        rows = self._fetch_all(
            "SELECT * FROM periods WHERE school_year_id = ? ORDER BY sort_order",
            (school_year_id,),
        )
        return [Period.from_row(r) for r in rows]

    def get_by_id(self, period_id: int) -> Period | None:
        row = self._fetch_one("SELECT * FROM periods WHERE id = ?", (period_id,))
        return Period.from_row(row) if row else None

    def create(self, period: Period) -> int:
        cursor = self._execute(
            """INSERT INTO periods (school_year_id, name, start_date, end_date, sort_order)
               VALUES (?, ?, ?, ?, ?)""",
            (period.school_year_id, period.name, period.start_date, period.end_date, period.sort_order),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update(self, period: Period):
        self._execute(
            """UPDATE periods SET name=?, start_date=?, end_date=?, sort_order=? WHERE id=?""",
            (period.name, period.start_date, period.end_date, period.sort_order, period.id),
        )
        self.conn.commit()
