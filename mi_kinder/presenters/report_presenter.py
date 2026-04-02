"""Presenter para reportes PDF."""
import os
import sqlite3
from PyQt6.QtWidgets import QFileDialog
from mi_kinder.services.session import Session
from mi_kinder.services.report_service import ReportService
from mi_kinder.services.pdf_service import PDFService
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.views.reports.report_view import ReportView
from mi_kinder.views.components.confirmation_dialog import info, alert


class ReportPresenter:
    def __init__(self, view: ReportView, conn: sqlite3.Connection):
        self._view = view
        self._conn = conn
        self._report_svc = ReportService(conn)
        self._pdf_svc = PDFService()
        self._group_repo = GroupRepository(conn)
        self._student_repo = StudentRepository(conn)
        self._session = Session.get()

        view.generate_individual.connect(self._on_gen_individual)
        view.generate_group.connect(self._on_gen_group)
        view.generate_general.connect(self._on_gen_general)
        view.generate_boletas.connect(self._on_gen_boletas)
        view.ind_group_combo.currentIndexChanged.connect(self._on_ind_group_changed)

    def load(self):
        year = self._session.current_year
        if not year:
            return
        if self._session.is_directora:
            groups = self._group_repo.get_all(year.id)
        else:
            groups = self._group_repo.get_for_user(year.id, self._session.current_user.id)
        self._view.load_groups(groups)

    def _on_ind_group_changed(self, index):
        gid = self._view.ind_group_combo.currentData()
        if gid:
            students = self._student_repo.get_by_group(gid)
            self._view.load_students(students)

    def _on_gen_individual(self, student_id: int):
        year = self._session.current_year
        if not year:
            alert(self._view, "Error", "No hay ciclo escolar activo.")
            return
        data = self._report_svc.get_individual_report_data(student_id, year.id)
        if not data:
            return
        path, _ = QFileDialog.getSaveFileName(
            self._view, "Guardar Reporte", f"reporte_{data['student'].full_name}.pdf", "PDF (*.pdf)"
        )
        if path:
            self._pdf_svc.generate_individual_report(data, path)
            info(self._view, "Reporte generado", f"Guardado en:\n{path}")
            self._open_file(path)

    def _on_gen_group(self, group_id: int):
        year = self._session.current_year
        if not year:
            return
        data = self._report_svc.get_group_report_data(group_id, year.id)
        if not data:
            return
        path, _ = QFileDialog.getSaveFileName(
            self._view, "Guardar Reporte Grupal",
            f"reporte_grupo_{data['group'].name}.pdf", "PDF (*.pdf)"
        )
        if path:
            self._pdf_svc.generate_group_report(data, path)
            info(self._view, "Reporte generado", f"Guardado en:\n{path}")
            self._open_file(path)

    def _on_gen_general(self):
        year = self._session.current_year
        if not year:
            return
        data = self._report_svc.get_general_report_data(year.id)
        path, _ = QFileDialog.getSaveFileName(
            self._view, "Guardar Reporte General", "reporte_general.pdf", "PDF (*.pdf)"
        )
        if path:
            self._pdf_svc.generate_general_report(data, path)
            info(self._view, "Reporte generado", f"Guardado en:\n{path}")
            self._open_file(path)

    def _on_gen_boletas(self, group_id: int):
        year = self._session.current_year
        if not year:
            return

        dir_path = QFileDialog.getExistingDirectory(
            self._view, "Carpeta para boletas"
        )
        if not dir_path:
            return

        students = self._student_repo.get_by_group(group_id)
        count = 0
        for s in students:
            data = self._report_svc.get_individual_report_data(s.id, year.id)
            if data:
                fname = f"boleta_{s.last_name}_{s.first_name}.pdf".replace(" ", "_")
                out = os.path.join(dir_path, fname)
                self._pdf_svc.generate_boleta(data, out)
                count += 1

        info(self._view, "Boletas generadas", f"{count} boletas guardadas en:\n{dir_path}")

    @staticmethod
    def _open_file(path: str):
        try:
            os.startfile(path)
        except Exception:
            pass
