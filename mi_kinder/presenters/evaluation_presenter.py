"""Presenter para captura de evaluaciones."""
import sqlite3
from mi_kinder.services.session import Session
from mi_kinder.repositories.evaluation_repository import (
    EvaluationRepository, EvaluationAreaRepository, GradingScaleRepository,
)
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.repositories.school_year_repository import PeriodRepository
from mi_kinder.models.evaluation import Evaluation
from mi_kinder.views.evaluations.evaluation_grid_view import EvaluationGridView
from mi_kinder.views.evaluations.area_management_view import AreaManagementWidget
from mi_kinder.views.settings.scale_management_view import ScaleManagementWidget
from mi_kinder.models.evaluation import EvaluationArea, GradingScale, GradingScaleLevel
from mi_kinder.views.components.confirmation_dialog import info


class EvaluationPresenter:
    def __init__(self, grid_view: EvaluationGridView, conn: sqlite3.Connection):
        self._view = grid_view
        self._conn = conn
        self._eval_repo = EvaluationRepository(conn)
        self._area_repo = EvaluationAreaRepository(conn)
        self._scale_repo = GradingScaleRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._period_repo = PeriodRepository(conn)
        self._session = Session.get()

        self._current_group_id: int | None = None
        self._current_period_id: int | None = None
        self._default_scale = None

        grid_view.group_changed.connect(self._on_group_changed)
        grid_view.period_changed.connect(self._on_period_changed)
        grid_view.save_requested.connect(self._on_save)
        grid_view.export_excel_requested.connect(self._on_export_excel)

    def load(self):
        year = self._session.current_year
        if not year:
            return

        # Cargar grupos segun permisos
        if self._session.is_directora:
            groups = self._group_repo.get_all(year.id)
        else:
            groups = self._group_repo.get_for_user(
                year.id, self._session.current_user.id
            )
        self._view.load_groups(groups)

        periods = self._period_repo.get_by_school_year(year.id)
        self._view.load_periods(periods)

        self._default_scale = self._scale_repo.get_default()

    def _on_group_changed(self, group_id: int):
        self._current_group_id = group_id
        self._refresh_grid()

    def _on_period_changed(self, period_id: int):
        self._current_period_id = period_id
        self._refresh_grid()

    def _refresh_grid(self):
        if not self._current_group_id or not self._current_period_id:
            return
        year = self._session.current_year
        if not year:
            return

        students = self._student_repo.get_by_group(self._current_group_id)
        areas = self._area_repo.get_by_school_year(year.id)

        scale = self._default_scale
        levels = scale.levels if scale else []

        evals = self._eval_repo.get_for_group_period(
            self._current_group_id, self._current_period_id
        )

        self._view.setup_grid(students, areas, levels, evals)

    def _on_save(self, results: list[dict]):
        if not self._default_scale:
            return
        count = 0
        for r in results:
            ev = Evaluation(
                student_id=r["student_id"],
                evaluation_area_id=r["area_id"],
                period_id=self._current_period_id,
                grading_scale_id=self._default_scale.id,
                grade_level_id=r["grade_level_id"],
                numeric_value=r["numeric_value"],
                evaluated_by=self._session.current_user.id if self._session.current_user else None,
            )
            self._eval_repo.upsert(ev)
            count += 1

        self._view.show_saved(count)

    def _on_export_excel(self):
        if not self._current_group_id or not self._current_period_id:
            return
        try:
            from openpyxl import Workbook
            from PyQt6.QtWidgets import QFileDialog
            year = self._session.current_year
            if not year:
                return
            students = self._student_repo.get_by_group(self._current_group_id)
            areas = self._area_repo.get_by_school_year(year.id)
            evals = self._eval_repo.get_for_group_period(
                self._current_group_id, self._current_period_id
            )
            eval_map = {(e.student_id, e.evaluation_area_id): e for e in evals}

            wb = Workbook()
            ws = wb.active
            ws.title = "Evaluaciones"
            ws.append(["Alumno"] + [a.name for a in areas])

            for s in students:
                row = [s.full_name]
                for a in areas:
                    ev = eval_map.get((s.id, a.id))
                    row.append(ev.grade_label if ev and ev.grade_label else "")
                ws.append(row)

            path, _ = QFileDialog.getSaveFileName(
                self._view, "Guardar Excel", "evaluaciones.xlsx", "Excel (*.xlsx)"
            )
            if path:
                wb.save(path)
                info(self._view, "Exportado", f"Archivo guardado en:\n{path}")
        except ImportError:
            info(self._view, "Error", "Se requiere openpyxl para exportar a Excel.")


class AreaPresenter:
    def __init__(self, widget: AreaManagementWidget, conn: sqlite3.Connection):
        self._widget = widget
        self._area_repo = EvaluationAreaRepository(conn)
        self._session = Session.get()

        widget.area_created.connect(self._on_create)
        widget.area_updated.connect(self._on_update)

    def load(self):
        year = self._session.current_year
        if not year:
            return
        areas = self._area_repo.get_by_school_year(year.id, active_only=False)
        self._widget.load_areas(areas)

    def _on_create(self, data: dict):
        year = self._session.current_year
        if not year:
            return
        existing = self._area_repo.get_by_school_year(year.id, active_only=False)
        area = EvaluationArea(
            school_year_id=year.id,
            name=data["name"],
            description=data["description"],
            sort_order=len(existing),
            is_active=data["is_active"],
        )
        self._area_repo.create(area)
        self.load()

    def _on_update(self, area_id: int, data: dict):
        row = self._area_repo._fetch_one(
            "SELECT * FROM evaluation_areas WHERE id = ?", (area_id,)
        )
        if not row:
            return
        area = EvaluationArea.from_row(row)
        area.name = data["name"]
        area.description = data["description"]
        area.is_active = data["is_active"]
        self._area_repo.update(area)
        self.load()


class ScalePresenter:
    def __init__(self, widget: ScaleManagementWidget, conn: sqlite3.Connection):
        self._widget = widget
        self._scale_repo = GradingScaleRepository(conn)
        self._session = Session.get()

        widget.scale_created.connect(self._on_create)

    def load(self):
        year = self._session.current_year
        year_id = year.id if year else None
        scales = self._scale_repo.get_all(year_id)
        self._widget.load_scales(scales)

    def _on_create(self, data: dict):
        year = self._session.current_year
        scale = GradingScale(
            name=data["name"],
            scale_type=data["scale_type"],
            school_year_id=year.id if year else None,
        )
        levels = []
        for l in data["levels"]:
            levels.append(GradingScaleLevel(
                label=l["label"],
                numeric_value=l["numeric_value"],
                color=l["color"],
                sort_order=l["sort_order"],
            ))
        self._scale_repo.create(scale, levels)
        self.load()
