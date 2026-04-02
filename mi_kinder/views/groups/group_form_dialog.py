"""Dialogo para crear/editar un grupo."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QPushButton, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from mi_kinder.models.group import Group
from mi_kinder.models.user import User
from mi_kinder.theme.colors import *


class GroupFormDialog(QDialog):
    def __init__(self, parent=None, group: Group | None = None, teachers: list[User] = []):
        super().__init__(parent)
        self._group = group
        self._teachers = teachers
        self._setup_ui()
        if group:
            self._load(group)

    def _setup_ui(self):
        title = "Editar Grupo" if self._group else "Nuevo Grupo"
        self.setWindowTitle(title)
        self.setMinimumWidth(380)
        self.setModal(True)
        self.setStyleSheet(f"""
            QLineEdit, QDateEdit, QComboBox, QSpinBox {{
                background-color: {BG_INPUT};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER};
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 13px;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Titulo
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(lbl)

        # Formulario
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Kinder 1A")
        self.name_input.setMinimumHeight(38)
        form.addRow("Nombre *:", self.name_input)

        self.grade_input = QLineEdit()
        self.grade_input.setPlaceholderText("Ej: 1, 2, 3")
        self.grade_input.setMinimumHeight(38)
        form.addRow("Nivel:", self.grade_input)

        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(0, 60)
        self.capacity_input.setSpecialValueText("Sin limite")
        self.capacity_input.setMinimumHeight(38)
        form.addRow("Capacidad:", self.capacity_input)

        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("— Sin asignar —", None)
        for t in self._teachers:
            self.teacher_combo.addItem(t.full_name, t.id)
        self.teacher_combo.setMinimumHeight(38)
        form.addRow("Maestra:", self.teacher_combo)

        layout.addLayout(form)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setFixedSize(120, 38)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {PRIMARY};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Guardar")
        save_btn.setFixedSize(120, 38)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
        """)
        save_btn.clicked.connect(self._validate_and_accept)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _load(self, group: Group):
        self.name_input.setText(group.name)
        self.grade_input.setText(group.grade_level or "")
        self.capacity_input.setValue(group.capacity or 0)

    def _validate_and_accept(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet(f"border: 2px solid {ERROR};")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "grade_level": self.grade_input.text().strip(),
            "capacity": self.capacity_input.value() or None,
            "teacher_id": self.teacher_combo.currentData(),
        }
