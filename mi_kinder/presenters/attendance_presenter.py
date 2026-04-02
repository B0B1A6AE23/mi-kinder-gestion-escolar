"""Presenter para asistencia."""
import sqlite3
from mi_kinder.services.session import Session
from mi_kinder.repositories.attendance_repository import AttendanceRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.models.attendance import AttendanceRecord
from mi_kinder.views.attendance.attendance_view import AttendanceView


class AttendancePresenter:
    def __init__(self, view: AttendanceView, conn: sqlite3.Connection):
        self._view = view
        self._conn = conn
        self._att_repo = AttendanceRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._session = Session.get()

        self._current_group_id: int | None = None

        view.group_changed.connect(self._on_group_changed)
        view.date_changed.connect(self._on_date_changed)
        view.save_requested.connect(self._on_save)

    def load(self):
        year = self._session.current_year
        if not year:
            return
        if self._session.is_directora:
            groups = self._group_repo.get_all(year.id)
        else:
            groups = self._group_repo.get_for_user(year.id, self._session.current_user.id)
        self._view.load_groups(groups)

    def _on_group_changed(self, group_id: int):
        self._current_group_id = group_id
        self._refresh()

    def _on_date_changed(self, date_str: str):
        self._refresh()

    def _refresh(self):
        if not self._current_group_id:
            return
        date_str = self._view.get_current_date_str()
        students = self._student_repo.get_by_group(self._current_group_id)
        records = self._att_repo.get_by_group_date(self._current_group_id, date_str)
        self._view.setup_grid(students, records)

    def _on_save(self, results: list[dict]):
        for r in results:
            rec = AttendanceRecord(
                student_id=r["student_id"],
                date=r["date"],
                status=r["status"],
                notes=r["notes"],
                recorded_by=self._session.current_user.id if self._session.current_user else None,
            )
            self._att_repo.upsert(rec)
        self._view.show_saved()
