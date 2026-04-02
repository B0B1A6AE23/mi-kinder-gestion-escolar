"""Dialogo para crear/editar alumno."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea,
    QLineEdit, QComboBox, QDialogButtonBox, QLabel, QWidget,
    QDateEdit, QTextEdit, QGroupBox,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from mi_kinder.models.student import Student
from mi_kinder.models.group import Group
from mi_kinder.views.components.photo_widget import PhotoWidget
from mi_kinder.theme.colors import *


class StudentFormDialog(QDialog):
    def __init__(self, parent=None, student: Student | None = None, groups: list[Group] = []):
        super().__init__(parent)
        self._student = student
        self._groups = groups
        self._photo_path = ""
        self._setup_ui()
        if student:
            self._load(student)

    def _setup_ui(self):
        title = "Editar Alumno" if self._student else "Nuevo Alumno"
        self.setWindowTitle(title)
        self.setMinimumWidth(560)
        self.setMinimumHeight(600)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background-color: {PRIMARY}; border-radius: 0px;")
        header.setFixedHeight(60)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setStyleSheet("color: white; background: transparent;")
        h_layout.addWidget(lbl)
        outer.addWidget(header)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)

        content = QWidget()
        content.setStyleSheet(f"background-color: {BG_MAIN};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # Foto + datos basicos en horizontal
        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        self.photo_widget = PhotoWidget(size=100)
        if self._student:
            self.photo_widget.set_photo(self._student.photo_path)
        self.photo_widget.photo_changed.connect(lambda p: setattr(self, "_photo_path", p))
        top_row.addWidget(self.photo_widget)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Datos personales
        personal_box = QGroupBox("Datos Personales")
        personal_box.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form1 = QFormLayout(personal_box)
        form1.setSpacing(10)

        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Nombre(s)")
        self.first_name.setMinimumHeight(36)
        form1.addRow("Nombre(s) *:", self.first_name)

        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Apellido paterno")
        self.last_name.setMinimumHeight(36)
        form1.addRow("Ap. Paterno *:", self.last_name)

        self.second_last_name = QLineEdit()
        self.second_last_name.setPlaceholderText("Apellido materno")
        self.second_last_name.setMinimumHeight(36)
        form1.addRow("Ap. Materno:", self.second_last_name)

        self.gender_combo = QComboBox()
        self.gender_combo.addItem("— No especificado —", None)
        self.gender_combo.addItem("Niño", "M")
        self.gender_combo.addItem("Niña", "F")
        self.gender_combo.setMinimumHeight(36)
        form1.addRow("Genero:", self.gender_combo)

        self.birth_date = QDateEdit()
        self.birth_date.setDisplayFormat("dd/MM/yyyy")
        self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate.currentDate().addYears(-4))
        self.birth_date.setMinimumHeight(36)
        form1.addRow("Fecha de nacimiento:", self.birth_date)

        self.curp = QLineEdit()
        self.curp.setPlaceholderText("CURP (opcional)")
        self.curp.setMaxLength(18)
        self.curp.setMinimumHeight(36)
        form1.addRow("CURP:", self.curp)

        self.group_combo = QComboBox()
        for g in self._groups:
            self.group_combo.addItem(g.name, g.id)
        self.group_combo.setMinimumHeight(36)
        form1.addRow("Grupo *:", self.group_combo)

        layout.addWidget(personal_box)

        # Datos del tutor
        guardian_box = QGroupBox("Datos del Tutor")
        guardian_box.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form2 = QFormLayout(guardian_box)
        form2.setSpacing(10)

        self.guardian_name = QLineEdit()
        self.guardian_name.setPlaceholderText("Nombre completo")
        self.guardian_name.setMinimumHeight(36)
        form2.addRow("Nombre del tutor:", self.guardian_name)

        self.guardian_phone = QLineEdit()
        self.guardian_phone.setPlaceholderText("Telefono")
        self.guardian_phone.setMinimumHeight(36)
        form2.addRow("Telefono:", self.guardian_phone)

        self.guardian_email = QLineEdit()
        self.guardian_email.setPlaceholderText("correo@ejemplo.com")
        self.guardian_email.setMinimumHeight(36)
        form2.addRow("Correo:", self.guardian_email)

        layout.addWidget(guardian_box)

        # Datos medicos
        medical_box = QGroupBox("Informacion Medica")
        medical_box.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form3 = QFormLayout(medical_box)
        form3.setSpacing(10)

        self.blood_type = QComboBox()
        for bt in ["— No especificado —", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            self.blood_type.addItem(bt, None if bt.startswith("—") else bt)
        self.blood_type.setMinimumHeight(36)
        form3.addRow("Tipo de sangre:", self.blood_type)

        self.allergies = QLineEdit()
        self.allergies.setPlaceholderText("Alergias conocidas")
        self.allergies.setMinimumHeight(36)
        form3.addRow("Alergias:", self.allergies)

        self.medical_notes = QTextEdit()
        self.medical_notes.setPlaceholderText("Notas medicas adicionales...")
        self.medical_notes.setFixedHeight(60)
        form3.addRow("Notas:", self.medical_notes)

        layout.addWidget(medical_box)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # Botones
        btn_bar = QWidget()
        btn_bar.setStyleSheet(f"background-color: {BG_CARD}; border-top: 1px solid {BORDER};")
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(24, 12, 24, 12)
        btn_layout.addStretch()

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

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        outer.addWidget(btn_bar)

    def _load(self, s: Student):
        self.first_name.setText(s.first_name)
        self.last_name.setText(s.last_name)
        self.second_last_name.setText(s.second_last_name or "")
        self.curp.setText(s.curp or "")
        self.guardian_name.setText(s.guardian_name or "")
        self.guardian_phone.setText(s.guardian_phone or "")
        self.guardian_email.setText(s.guardian_email or "")
        self.allergies.setText(s.allergies or "")
        self.medical_notes.setPlainText(s.medical_notes or "")
        self._photo_path = s.photo_path or ""

        if s.gender:
            idx = self.gender_combo.findData(s.gender)
            if idx >= 0:
                self.gender_combo.setCurrentIndex(idx)

        if s.birth_date:
            try:
                from datetime import date
                d = date.fromisoformat(s.birth_date)
                self.birth_date.setDate(QDate(d.year, d.month, d.day))
            except Exception:
                pass

        if s.blood_type:
            idx = self.blood_type.findData(s.blood_type)
            if idx >= 0:
                self.blood_type.setCurrentIndex(idx)

        for i in range(self.group_combo.count()):
            if self.group_combo.itemData(i) == s.group_id:
                self.group_combo.setCurrentIndex(i)
                break

    def _validate_and_accept(self):
        ok = True
        if not self.first_name.text().strip():
            self.first_name.setStyleSheet(f"border: 2px solid {ERROR};")
            ok = False
        if not self.last_name.text().strip():
            self.last_name.setStyleSheet(f"border: 2px solid {ERROR};")
            ok = False
        if ok:
            self.accept()

    def get_data(self) -> dict:
        bd = self.birth_date.date()
        return {
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "second_last_name": self.second_last_name.text().strip(),
            "curp": self.curp.text().strip().upper(),
            "birth_date": f"{bd.year():04d}-{bd.month():02d}-{bd.day():02d}",
            "gender": self.gender_combo.currentData(),
            "group_id": self.group_combo.currentData(),
            "guardian_name": self.guardian_name.text().strip(),
            "guardian_phone": self.guardian_phone.text().strip(),
            "guardian_email": self.guardian_email.text().strip(),
            "blood_type": self.blood_type.currentData(),
            "allergies": self.allergies.text().strip(),
            "medical_notes": self.medical_notes.toPlainText().strip(),
            "photo_path": self._photo_path,
        }
