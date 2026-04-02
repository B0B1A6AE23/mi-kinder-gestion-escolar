"""Presenter para ajustes del sistema."""
import sqlite3
from mi_kinder.services.session import Session
from mi_kinder.repositories.school_year_repository import SchoolYearRepository, PeriodRepository
from mi_kinder.models.school_year import SchoolYear, Period
from mi_kinder.views.settings.settings_view import SettingsView, SchoolYearDialog, PeriodDialog
from mi_kinder.views.components.confirmation_dialog import info, alert
import zipfile, os, shutil
from datetime import datetime
from mi_kinder.config import get_data_dir, get_backups_dir, DB_FILENAME


class SettingsPresenter:
    def __init__(self, view: SettingsView, conn: sqlite3.Connection):
        self._view = view
        self._year_repo = SchoolYearRepository(conn)
        self._period_repo = PeriodRepository(conn)
        self._conn = conn
        self._session = Session.get()

        view.new_year_requested.connect(self._on_new_year)
        view.activate_year_requested.connect(self._on_activate_year)
        view.new_period_requested.connect(self._on_new_period)
        view.school_info_saved.connect(self._on_save_school_info)
        view.backup_requested.connect(self._on_backup)
        view.restore_requested.connect(self._on_restore)

    def load(self):
        years = self._year_repo.get_all()
        self._view.load_years(years)

        active = self._year_repo.get_active()
        if active:
            periods = self._period_repo.get_by_school_year(active.id)
            self._view.load_periods(periods, active.name)

        row = self._conn.execute("SELECT * FROM school_info WHERE id = 1").fetchone()
        if row:
            self._view.load_school_info(dict(row))

    def _on_new_year(self):
        dlg = SchoolYearDialog(self._view)
        if dlg.exec():
            data = dlg.get_data()
            year = SchoolYear(name=data["name"], start_date=data["start_date"], end_date=data["end_date"])
            year_id = self._year_repo.create(year)

            # Si no hay ciclo activo, activar este automaticamente
            active = self._year_repo.get_active()
            if not active:
                self._year_repo.set_active(year_id)
                new_year = self._year_repo.get_by_id(year_id)
                self._session.current_year = new_year

            self.load()

    def _on_activate_year(self, year_id: int):
        self._year_repo.set_active(year_id)
        year = self._year_repo.get_by_id(year_id)
        self._session.current_year = year
        self.load()
        info(self._view, "Ciclo Activado", f"El ciclo '{year.name}' ahora esta activo.")

    def _on_new_period(self):
        active = self._year_repo.get_active()
        if not active:
            alert(self._view, "Sin ciclo activo", "Primero activa un ciclo escolar.")
            return
        dlg = PeriodDialog(self._view)
        if dlg.exec():
            data = dlg.get_data()
            existing = self._period_repo.get_by_school_year(active.id)
            period = Period(
                school_year_id=active.id,
                name=data["name"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                sort_order=len(existing),
            )
            self._period_repo.create(period)
            self.load()

    def _on_save_school_info(self, data: dict):
        self._conn.execute(
            """UPDATE school_info SET name=?, address=?, phone=?, director_name=? WHERE id=1""",
            (data["name"], data["address"], data["phone"], data["director_name"]),
        )
        self._conn.commit()
        info(self._view, "Guardado", "Informacion de la escuela actualizada.")

    def _on_backup(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(get_backups_dir(), f"backup_{ts}.zip")
        data_dir = get_data_dir()
        db_path = os.path.join(data_dir, DB_FILENAME)
        photos_dir = os.path.join(data_dir, "photos")

        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(db_path):
                zf.write(db_path, DB_FILENAME)
            if os.path.exists(photos_dir):
                for fname in os.listdir(photos_dir):
                    zf.write(os.path.join(photos_dir, fname), os.path.join("photos", fname))

        info(self._view, "Respaldo creado",
             f"Respaldo guardado en:\n{backup_path}")

    def _on_restore(self):
        from PyQt6.QtWidgets import QFileDialog
        from mi_kinder.views.components.confirmation_dialog import confirm
        path, _ = QFileDialog.getOpenFileName(
            self._view, "Seleccionar respaldo", get_backups_dir(), "ZIP (*.zip)"
        )
        if not path:
            return
        if not confirm(self._view, "Restaurar respaldo",
                       "Esto reemplazara TODOS los datos actuales con el respaldo.\n¿Continuar?"):
            return

        data_dir = get_data_dir()
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(data_dir)

        info(self._view, "Restaurado",
             "Respaldo restaurado. Reinicia la aplicacion para aplicar los cambios.")
