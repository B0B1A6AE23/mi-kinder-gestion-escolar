"""Repositorio de observaciones."""
import sqlite3
from mi_kinder.models.observation import StudentObservation
from mi_kinder.repositories.base_repository import BaseRepository


class ObservationRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "student_observations")

    def get_by_student(self, student_id: int) -> list[StudentObservation]:
        rows = self._fetch_all(
            "SELECT * FROM student_observations WHERE student_id = ? ORDER BY created_at DESC",
            (student_id,),
        )
        return [StudentObservation.from_row(r) for r in rows]

    def get_by_student_period(self, student_id: int, period_id: int) -> list[StudentObservation]:
        rows = self._fetch_all(
            """SELECT * FROM student_observations
               WHERE student_id = ? AND period_id = ? ORDER BY created_at DESC""",
            (student_id, period_id),
        )
        return [StudentObservation.from_row(r) for r in rows]

    def create(self, obs: StudentObservation) -> int:
        cursor = self._execute(
            """INSERT INTO student_observations (student_id, period_id, content, category, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            (obs.student_id, obs.period_id, obs.content, obs.category, obs.created_by),
        )
        self.conn.commit()
        return cursor.lastrowid
