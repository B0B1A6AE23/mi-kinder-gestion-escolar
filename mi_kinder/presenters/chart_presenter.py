"""Presenter para graficas."""
import os
import sqlite3
from PyQt6.QtWidgets import QFileDialog
from mi_kinder.services.session import Session
from mi_kinder.services.chart_service import ChartService
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.repositories.school_year_repository import PeriodRepository
from mi_kinder.views.charts.chart_view import ChartView
from mi_kinder.views.components.confirmation_dialog import info


class ChartPresenter:
    def __init__(self, view: ChartView, conn: sqlite3.Connection):
        self._view = view
        self._conn = conn
        self._chart_svc = ChartService(conn)
        self._group_repo = GroupRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._period_repo = PeriodRepository(conn)
        self._session = Session.get()

        self._current_grp_group_id = None
        self._current_grp_period_id = None

        view.ind_group_changed.connect(self._on_ind_group_changed)
        view.ind_student_selected.connect(self._on_ind_student_selected)
        view.grp_group_changed.connect(self._on_grp_group_changed)
        view.grp_period_changed.connect(self._on_grp_period_changed)
        view.gen_requested.connect(self._on_gen_requested)
        view.export_requested.connect(self._on_export)

    def load(self):
        year = self._session.current_year
        if not year:
            return
        if self._session.is_directora:
            groups = self._group_repo.get_all(year.id)
        else:
            groups = self._group_repo.get_for_user(year.id, self._session.current_user.id)
        self._view.load_groups(groups)

        periods = self._period_repo.get_by_school_year(year.id)
        self._view.load_periods(periods)

    def _on_ind_group_changed(self, group_id: int):
        students = self._student_repo.get_by_group(group_id)
        self._view.load_students(students)

    def _on_ind_student_selected(self, student_id: int):
        year = self._session.current_year
        if not year:
            return
        data = self._chart_svc.get_student_progress_data(student_id, year.id)
        if data and data["student"]:
            self._view.draw_progress_line(
                data["period_names"],
                data["series"],
                data["student"].full_name,
            )

    def _on_grp_group_changed(self, group_id: int):
        self._current_grp_group_id = group_id
        self._try_draw_group()

    def _on_grp_period_changed(self, period_id: int):
        self._current_grp_period_id = period_id
        self._try_draw_group()

    def _try_draw_group(self):
        gid = self._current_grp_group_id
        pid = self._current_grp_period_id
        if not gid or not pid:
            return
        year = self._session.current_year
        if not year:
            return

        group = self._group_repo.get_by_id(gid)
        bar_data = self._chart_svc.get_group_bar_data(gid, pid)
        self._view.draw_group_bars(
            bar_data["area_names"],
            bar_data["averages"],
            group.name if group else "",
        )

    def _on_gen_requested(self):
        year = self._session.current_year
        if not year:
            return
        data = self._chart_svc.get_general_comparison_data(year.id)
        self._view.draw_general_heatmap(
            data["group_names"],
            data["area_names"],
            data["matrix"],
        )

    def _on_export(self, fmt: str):
        canvas = self._view.ind_canvas
        path, _ = QFileDialog.getSaveFileName(
            self._view, "Guardar grafica", "grafica.png", "PNG (*.png)"
        )
        if path:
            canvas.fig.savefig(path, dpi=150, bbox_inches="tight")
            info(self._view, "Guardada", f"Grafica guardada en:\n{path}")
