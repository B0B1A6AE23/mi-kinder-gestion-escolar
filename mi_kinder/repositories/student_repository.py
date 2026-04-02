"""Repositorio de alumnos."""
import sqlite3
from mi_kinder.models.student import Student, StudentTransfer
from mi_kinder.repositories.base_repository import BaseRepository


class StudentRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "students")

    def get_by_group(self, group_id: int, active_only: bool = True) -> list[Student]:
        sql = """SELECT s.*, g.name as group_name FROM students s
                 JOIN groups_ g ON g.id = s.group_id
                 WHERE s.group_id = ?"""
        if active_only:
            sql += " AND s.is_active = 1"
        sql += " ORDER BY s.last_name, s.first_name"
        return [Student.from_row(r) for r in self._fetch_all(sql, (group_id,))]

    def get_by_id(self, student_id: int) -> Student | None:
        row = self._fetch_one(
            """SELECT s.*, g.name as group_name FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE s.id = ?""",
            (student_id,),
        )
        return Student.from_row(row) if row else None

    def search(self, query: str, school_year_id: int) -> list[Student]:
        pattern = f"%{query}%"
        sql = """SELECT s.*, g.name as group_name FROM students s
                 JOIN groups_ g ON g.id = s.group_id
                 WHERE g.school_year_id = ? AND s.is_active = 1
                 AND (s.first_name LIKE ? OR s.last_name LIKE ? OR s.second_last_name LIKE ?)
                 ORDER BY s.last_name, s.first_name LIMIT 50"""
        return [Student.from_row(r) for r in self._fetch_all(
            sql, (school_year_id, pattern, pattern, pattern)
        )]

    def create(self, student: Student) -> int:
        cursor = self._execute(
            """INSERT INTO students (group_id, first_name, last_name, second_last_name,
               curp, birth_date, gender, photo_path, enrollment_date,
               guardian_name, guardian_phone, guardian_email, address,
               blood_type, allergies, medical_notes, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (student.group_id, student.first_name, student.last_name,
             student.second_last_name or None, student.curp or None,
             student.birth_date or None, student.gender,
             student.photo_path or None, student.enrollment_date,
             student.guardian_name or None, student.guardian_phone or None,
             student.guardian_email or None, student.address or None,
             student.blood_type or None, student.allergies or None,
             student.medical_notes or None, int(student.is_active)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update(self, student: Student):
        self._execute(
            """UPDATE students SET group_id=?, first_name=?, last_name=?,
               second_last_name=?, curp=?, birth_date=?, gender=?, photo_path=?,
               guardian_name=?, guardian_phone=?, guardian_email=?, address=?,
               blood_type=?, allergies=?, medical_notes=?, is_active=?,
               updated_at=datetime('now') WHERE id=?""",
            (student.group_id, student.first_name, student.last_name,
             student.second_last_name or None, student.curp or None,
             student.birth_date or None, student.gender,
             student.photo_path or None,
             student.guardian_name or None, student.guardian_phone or None,
             student.guardian_email or None, student.address or None,
             student.blood_type or None, student.allergies or None,
             student.medical_notes or None, int(student.is_active), student.id),
        )
        self.conn.commit()

    def transfer(self, student_id: int, to_group_id: int, reason: str, user_id: int | None):
        student = self.get_by_id(student_id)
        if not student:
            return
        from_group_id = student.group_id
        self._execute(
            "UPDATE students SET group_id=?, updated_at=datetime('now') WHERE id=?",
            (to_group_id, student_id),
        )
        self._execute(
            """INSERT INTO student_transfers (student_id, from_group_id, to_group_id, reason, transferred_by)
               VALUES (?, ?, ?, ?, ?)""",
            (student_id, from_group_id, to_group_id, reason or None, user_id),
        )
        self.conn.commit()

    def count_by_group(self, group_id: int) -> int:
        row = self._fetch_one(
            "SELECT COUNT(*) as cnt FROM students WHERE group_id = ? AND is_active = 1",
            (group_id,),
        )
        return row["cnt"] if row else 0

    def count_all(self, school_year_id: int) -> int:
        row = self._fetch_one(
            """SELECT COUNT(*) as cnt FROM students s
               JOIN groups_ g ON g.id = s.group_id
               WHERE g.school_year_id = ? AND s.is_active = 1""",
            (school_year_id,),
        )
        return row["cnt"] if row else 0
