"""Repositorio de asistencia."""
import sqlite3
from mi_kinder.models.attendance import AttendanceRecord
from mi_kinder.repositories.base_repository import BaseRepository


class AttendanceRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "attendance_records")

    def get_by_group_date(self, group_id: int, date: str) -> list[AttendanceRecord]:
        rows = self._fetch_all(
            """SELECT ar.* FROM attendance_records ar
               JOIN students s ON s.id = ar.student_id
               WHERE s.group_id = ? AND ar.date = ?
               ORDER BY s.last_name, s.first_name""",
            (group_id, date),
        )
        return [AttendanceRecord.from_row(r) for r in rows]

    def upsert(self, record: AttendanceRecord) -> int:
        existing = self._fetch_one(
            "SELECT id FROM attendance_records WHERE student_id=? AND date=?",
            (record.student_id, record.date),
        )
        if existing:
            self._execute(
                """UPDATE attendance_records SET status=?, notes=?, recorded_by=?
                   WHERE id=?""",
                (record.status, record.notes or None, record.recorded_by, existing["id"]),
            )
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self._execute(
                """INSERT INTO attendance_records (student_id, date, status, notes, recorded_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (record.student_id, record.date, record.status,
                 record.notes or None, record.recorded_by),
            )
            self.conn.commit()
            return cursor.lastrowid

    def get_attendance_rate(self, group_id: int, start_date: str, end_date: str) -> float:
        row = self._fetch_one(
            """SELECT
                 COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as rate
               FROM attendance_records ar
               JOIN students s ON s.id = ar.student_id
               WHERE s.group_id = ? AND ar.date BETWEEN ? AND ?""",
            (group_id, start_date, end_date),
        )
        return row["rate"] if row and row["rate"] else 0.0
