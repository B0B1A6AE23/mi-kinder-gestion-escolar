"""Gestion de areas de evaluacion (tab en Ajustes)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.models.evaluation import EvaluationArea
from mi_kinder.theme.colors import *


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


class AreaDialog(QDialog):
    def __init__(self, parent=None, area: EvaluationArea | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Area" if not area else "Editar Area")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._area = area
        self._setup_ui()
        if area:
            self._load(area)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Lenguaje y comunicacion")
        self.name_input.setMinimumHeight(36)
        form.addRow("Nombre *:", self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descripcion del area (opcional)")
        self.desc_input.setFixedHeight(80)
        form.addRow("Descripcion:", self.desc_input)

        self.active_check = QCheckBox("Area activa")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)

        layout.addLayout(form)

        row = QHBoxLayout()
        row.addStretch()
        cancel = _styled_secondary_btn("Cancelar", 110)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)
        save = _styled_primary_btn("Guardar", 110)
        save.clicked.connect(self._validate)
        row.addWidget(save)
        layout.addLayout(row)

    def _load(self, a: EvaluationArea):
        self.name_input.setText(a.name)
        self.desc_input.setPlainText(a.description or "")
        self.active_check.setChecked(a.is_active)

    def _validate(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet(f"border: 2px solid {ERROR};")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "is_active": self.active_check.isChecked(),
        }


class AreaManagementWidget(QWidget):
    area_created = pyqtSignal(dict)
    area_updated = pyqtSignal(int, dict)

    def __init__(self):
        super().__init__()
        self._areas: list[EvaluationArea] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        info_lbl = QLabel("Areas de evaluacion del ciclo activo:")
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(info_lbl)

        btn_row = QHBoxLayout()
        new_btn = _styled_primary_btn("+ Nueva Area", 160)
        new_btn.clicked.connect(self._on_new)
        btn_row.addWidget(new_btn)

        edit_btn = _styled_secondary_btn("✏️ Editar", 120)
        edit_btn.clicked.connect(self._on_edit)
        btn_row.addWidget(edit_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.area_list = QListWidget()
        self.area_list.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {BORDER}; border-radius: 8px; background: {BG_CARD}; color: {TEXT_PRIMARY}; }}
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid {BORDER}; color: {TEXT_PRIMARY}; }}
            QListWidget::item:selected {{ background-color: {PRIMARY_LIGHT}; color: {TEXT_PRIMARY}; }}
        """)
        layout.addWidget(self.area_list)

    def load_areas(self, areas: list[EvaluationArea]):
        self._areas = areas
        self.area_list.clear()
        for a in areas:
            status = "✅" if a.is_active else "❌"
            text = f"{status}  {a.name}"
            if a.description:
                text += f"  —  {a.description[:50]}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, a.id)
            self.area_list.addItem(item)

    def _on_new(self):
        dlg = AreaDialog(self)
        if dlg.exec():
            self.area_created.emit(dlg.get_data())

    def _on_edit(self):
        item = self.area_list.currentItem()
        if not item:
            return
        area_id = item.data(Qt.ItemDataRole.UserRole)
        area = next((a for a in self._areas if a.id == area_id), None)
        if not area:
            return
        dlg = AreaDialog(self, area)
        if dlg.exec():
            self.area_updated.emit(area_id, dlg.get_data())
