"""Vista de ajustes con tabs: Escuela, Ciclo Escolar, Periodos."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFormLayout, QLineEdit, QGroupBox, QListWidget,
    QListWidgetItem, QDialog, QDateEdit, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QFont
from mi_kinder.models.school_year import SchoolYear, Period
from mi_kinder.theme.colors import *

# ── Helpers de estilo ─────────────────────────────────────────

def _styled_primary_btn(text: str, min_w: int = 180) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(40)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            padding: 0 14px;
        }}
        QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
    """)
    return btn


def _styled_secondary_btn(text: str, min_w: int = 180) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(40)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {BG_CARD};
            color: {PRIMARY};
            border: 2px solid {PRIMARY};
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            padding: 0 14px;
        }}
        QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
    """)
    return btn


def _dialog_buttons(dialog: QDialog, on_save):
    """Agrega botones Cancelar/Guardar con estilo inline a un QDialog."""
    row = QHBoxLayout()
    row.addStretch()
    cancel = _styled_secondary_btn("Cancelar", 110)
    cancel.clicked.connect(dialog.reject)
    row.addWidget(cancel)
    save = _styled_primary_btn("Guardar", 110)
    save.clicked.connect(on_save)
    row.addWidget(save)
    return row


# ── SchoolYearDialog ──────────────────────────────────────────

class SchoolYearDialog(QDialog):
    def __init__(self, parent=None, year: SchoolYear | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Ciclo Escolar" if not year else "Editar Ciclo Escolar")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._year = year
        self._setup_ui()
        if year:
            self._load(year)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: 2026-2027")
        self.name_input.setMinimumHeight(36)
        form.addRow("Nombre *:", self.name_input)

        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumHeight(36)
        form.addRow("Fecha inicio *:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(10))
        self.end_date.setMinimumHeight(36)
        form.addRow("Fecha fin *:", self.end_date)

        layout.addLayout(form)
        layout.addLayout(_dialog_buttons(self, self._validate))

    def _load(self, y: SchoolYear):
        self.name_input.setText(y.name)
        try:
            from datetime import date
            d = date.fromisoformat(y.start_date)
            self.start_date.setDate(QDate(d.year, d.month, d.day))
            d2 = date.fromisoformat(y.end_date)
            self.end_date.setDate(QDate(d2.year, d2.month, d2.day))
        except Exception:
            pass

    def _validate(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet(f"border: 2px solid {ERROR};")
            return
        self.accept()

    def get_data(self) -> dict:
        sd = self.start_date.date()
        ed = self.end_date.date()
        return {
            "name": self.name_input.text().strip(),
            "start_date": f"{sd.year()}-{sd.month():02d}-{sd.day():02d}",
            "end_date": f"{ed.year()}-{ed.month():02d}-{ed.day():02d}",
        }


# ── PeriodDialog ──────────────────────────────────────────────

class PeriodDialog(QDialog):
    def __init__(self, parent=None, period: Period | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Periodo" if not period else "Editar Periodo")
        self.setMinimumWidth(340)
        self.setModal(True)
        self._period = period
        self._setup_ui()
        if period:
            self._load(period)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Trimestre 1")
        self.name_input.setMinimumHeight(36)
        form.addRow("Nombre *:", self.name_input)

        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumHeight(36)
        form.addRow("Inicio:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addMonths(3))
        self.end_date.setMinimumHeight(36)
        form.addRow("Fin:", self.end_date)

        layout.addLayout(form)
        layout.addLayout(_dialog_buttons(self, self._validate))

    def _validate(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet(f"border: 2px solid {ERROR};")
            return
        self.accept()

    def _load(self, p: Period):
        self.name_input.setText(p.name)
        try:
            from datetime import date
            d = date.fromisoformat(p.start_date)
            self.start_date.setDate(QDate(d.year, d.month, d.day))
            d2 = date.fromisoformat(p.end_date)
            self.end_date.setDate(QDate(d2.year, d2.month, d2.day))
        except Exception:
            pass

    def get_data(self) -> dict:
        sd = self.start_date.date()
        ed = self.end_date.date()
        return {
            "name": self.name_input.text().strip(),
            "start_date": f"{sd.year()}-{sd.month():02d}-{sd.day():02d}",
            "end_date": f"{ed.year()}-{ed.month():02d}-{ed.day():02d}",
        }


# ── SettingsView ──────────────────────────────────────────────

class SettingsView(QWidget):
    year_changed = pyqtSignal()
    new_year_requested = pyqtSignal()
    activate_year_requested = pyqtSignal(int)
    new_period_requested = pyqtSignal()
    school_info_saved = pyqtSignal(dict)
    backup_requested = pyqtSignal()
    restore_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Ajustes")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_school_tab(), "🏫 Escuela")
        self.tabs.addTab(self._build_years_tab(), "📅 Ciclos Escolares")
        self.tabs.addTab(self._build_periods_tab(), "🗓 Periodos")
        self.tabs.addTab(self._build_backup_tab(), "💾 Respaldo")
        layout.addWidget(self.tabs)

    def _build_school_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        box = QGroupBox("Informacion de la Escuela")
        box.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form = QFormLayout(box)
        form.setSpacing(10)

        self.school_name = QLineEdit()
        self.school_name.setMinimumHeight(36)
        form.addRow("Nombre:", self.school_name)

        self.school_address = QLineEdit()
        self.school_address.setMinimumHeight(36)
        form.addRow("Direccion:", self.school_address)

        self.school_phone = QLineEdit()
        self.school_phone.setMinimumHeight(36)
        form.addRow("Telefono:", self.school_phone)

        self.school_director = QLineEdit()
        self.school_director.setMinimumHeight(36)
        form.addRow("Directora:", self.school_director)

        layout.addWidget(box)

        save_btn = _styled_primary_btn("💾 Guardar Informacion", 220)
        save_btn.clicked.connect(self._on_save_school)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def _build_years_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        btn_row = QHBoxLayout()
        new_year_btn = _styled_primary_btn("+ Nuevo Ciclo Escolar", 200)
        new_year_btn.clicked.connect(self.new_year_requested.emit)
        btn_row.addWidget(new_year_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.years_list = QListWidget()
        self.years_list.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {BORDER}; border-radius: 8px; background: {BG_CARD}; }}
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background-color: {PRIMARY_LIGHT}; color: {TEXT_PRIMARY}; }}
        """)
        layout.addWidget(self.years_list)

        self.activate_year_btn = _styled_secondary_btn("✅ Activar ciclo seleccionado", 240)
        self.activate_year_btn.clicked.connect(self._on_activate_year)
        layout.addWidget(self.activate_year_btn)
        return w

    def _build_periods_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.periods_year_label = QLabel("Periodos del ciclo activo:")
        self.periods_year_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(self.periods_year_label)

        btn_row = QHBoxLayout()
        new_period_btn = _styled_primary_btn("+ Nuevo Periodo", 180)
        new_period_btn.clicked.connect(self.new_period_requested.emit)
        btn_row.addWidget(new_period_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.periods_list = QListWidget()
        self.periods_list.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {BORDER}; border-radius: 8px; background: {BG_CARD}; }}
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid {BORDER}; }}
        """)
        layout.addWidget(self.periods_list)
        return w

    def _build_backup_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        info_lbl = QLabel(
            "Los respaldos incluyen la base de datos y todas las fotos de alumnos.\n"
            "Se guardan como archivo .zip en la carpeta de respaldos."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(info_lbl)

        backup_btn = _styled_primary_btn("💾 Crear Respaldo Ahora", 250)
        backup_btn.clicked.connect(self.backup_requested.emit)
        layout.addWidget(backup_btn)

        restore_btn = _styled_secondary_btn("📂 Restaurar desde Respaldo", 250)
        restore_btn.clicked.connect(self.restore_requested.emit)
        layout.addWidget(restore_btn)

        layout.addStretch()
        return w

    def _on_save_school(self):
        self.school_info_saved.emit({
            "name": self.school_name.text().strip(),
            "address": self.school_address.text().strip(),
            "phone": self.school_phone.text().strip(),
            "director_name": self.school_director.text().strip(),
        })

    def _on_activate_year(self):
        item = self.years_list.currentItem()
        if item:
            self.activate_year_requested.emit(item.data(Qt.ItemDataRole.UserRole))

    def load_school_info(self, info: dict):
        self.school_name.setText(info.get("name", ""))
        self.school_address.setText(info.get("address", "") or "")
        self.school_phone.setText(info.get("phone", "") or "")
        self.school_director.setText(info.get("director_name", "") or "")

    def load_years(self, years: list[SchoolYear]):
        self.years_list.clear()
        for y in years:
            text = f"{'✅ ' if y.is_active else ''}  {y.name}  ({y.start_date} — {y.end_date})"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, y.id)
            self.years_list.addItem(item)

    def load_periods(self, periods: list[Period], year_name: str = ""):
        self.periods_year_label.setText(f"Periodos del ciclo: {year_name}")
        self.periods_list.clear()
        for p in periods:
            item = QListWidgetItem(f"  {p.name}  ({p.start_date} — {p.end_date})")
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            self.periods_list.addItem(item)
