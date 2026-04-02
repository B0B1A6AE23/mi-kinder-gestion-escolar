"""Ficha detalle de alumno con tabs."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QFormLayout, QGroupBox, QTextEdit, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.models.student import Student
from mi_kinder.models.evaluation import Evaluation
from mi_kinder.models.observation import StudentObservation
from mi_kinder.views.components.photo_widget import PhotoWidget
from mi_kinder.theme.colors import *


class StudentDetailView(QWidget):
    back_requested = pyqtSignal()
    edit_requested = pyqtSignal(int)

    def __init__(self, can_edit: bool = True):
        super().__init__()
        self._can_edit = can_edit
        self._student: Student | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        # Barra superior
        top_bar = QHBoxLayout()
        back_btn = QPushButton("← Regresar")
        back_btn.setFixedHeight(36)
        back_btn.setMinimumWidth(120)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {PRIMARY};
                border: 2px solid {PRIMARY};
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        top_bar.addWidget(back_btn)
        top_bar.addStretch()

        if self._can_edit:
            self.edit_btn = QPushButton("✏️ Editar")
            self.edit_btn.setFixedHeight(36)
            self.edit_btn.setMinimumWidth(100)
            self.edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0 12px;
                }}
                QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
            """)
            self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._student.id))
            top_bar.addWidget(self.edit_btn)

        layout.addLayout(top_bar)

        # Header del alumno
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 15px;
                border: 1px solid {BORDER};
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(20)

        self.photo = PhotoWidget(size=90, editable=False)
        header_layout.addWidget(self.photo)

        info_layout = QVBoxLayout()
        self.name_label = QLabel("—")
        self.name_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.name_label.setStyleSheet(f"color: {PRIMARY_DARK}; background: transparent;")
        info_layout.addWidget(self.name_label)

        self.detail_label = QLabel("—")
        self.detail_label.setFont(QFont("Segoe UI", 12))
        self.detail_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        info_layout.addWidget(self.detail_label)

        self.guardian_label = QLabel("—")
        self.guardian_label.setFont(QFont("Segoe UI", 12))
        self.guardian_label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        info_layout.addWidget(self.guardian_label)

        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_evaluations_tab(), "📝 Evaluaciones")
        self.tabs.addTab(self._build_observations_tab(), "💬 Observaciones")
        self.tabs.addTab(self._build_attendance_tab(), "📋 Asistencia")
        self.tabs.addTab(self._build_info_tab(), "ℹ️ Informacion")
        layout.addWidget(self.tabs)

    def _build_evaluations_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        self.eval_table = QTableWidget()
        self.eval_table.setColumnCount(4)
        self.eval_table.setHorizontalHeaderLabels(["Periodo", "Area", "Calificacion", "Observaciones"])
        self.eval_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.eval_table.setAlternatingRowColors(True)
        self.eval_table.verticalHeader().setVisible(False)
        self.eval_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.eval_table.setStyleSheet(f"""
            QTableWidget {{ border: none; alternate-background-color: {BG_INPUT}; color: {TEXT_PRIMARY}; }}
            QTableWidget::item {{ color: {TEXT_PRIMARY}; }}
            QHeaderView::section {{ background-color: {PRIMARY}; color: white; font-weight: bold; padding: 4px; border: none; }}
        """)
        layout.addWidget(self.eval_table)
        return w

    def _build_observations_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        self.obs_area = QTextEdit()
        self.obs_area.setReadOnly(True)
        self.obs_area.setStyleSheet(f"border: none; background-color: {BG_MAIN};")
        layout.addWidget(self.obs_area)
        return w

    def _build_attendance_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        self.att_label = QLabel("La vista de asistencia estara disponible en la proxima fase.")
        self.att_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.att_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 14px;")
        layout.addWidget(self.att_label)
        return w

    def _build_info_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        self.info_form = QFormLayout()
        self.info_form.setSpacing(8)
        self._info_fields: dict[str, QLabel] = {}
        for key in ["CURP", "Fecha de nacimiento", "Genero",
                    "Tipo de sangre", "Alergias", "Notas medicas",
                    "Direccion", "Correo tutor"]:
            lbl = QLabel("—")
            lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
            lbl.setWordWrap(True)
            self._info_fields[key] = lbl
            self.info_form.addRow(f"<b>{key}:</b>", lbl)

        layout.addLayout(self.info_form)
        layout.addStretch()
        scroll.setWidget(w)
        return scroll

    def load_student(self, student: Student):
        self._student = student
        self.photo.set_photo(student.photo_path)
        self.name_label.setText(student.full_name)

        gender = {"M": "Niño", "F": "Niña"}.get(student.gender or "", "—")
        self.detail_label.setText(
            f"📚 {student.group_name}   |   "
            f"🎂 {student.birth_date or '—'}   |   {gender}"
        )
        self.guardian_label.setText(
            f"👨‍👩‍👧 {student.guardian_name or '—'}   "
            f"📞 {student.guardian_phone or '—'}"
        )

        self._info_fields["CURP"].setText(student.curp or "—")
        self._info_fields["Fecha de nacimiento"].setText(student.birth_date or "—")
        self._info_fields["Genero"].setText(gender)
        self._info_fields["Tipo de sangre"].setText(student.blood_type or "—")
        self._info_fields["Alergias"].setText(student.allergies or "—")
        self._info_fields["Notas medicas"].setText(student.medical_notes or "—")
        self._info_fields["Direccion"].setText(student.address or "—")
        self._info_fields["Correo tutor"].setText(student.guardian_email or "—")

    def load_evaluations(self, evaluations: list[Evaluation]):
        self.eval_table.setRowCount(len(evaluations))
        for r, e in enumerate(evaluations):
            self.eval_table.setItem(r, 0, QTableWidgetItem(e.period_name))
            self.eval_table.setItem(r, 1, QTableWidgetItem(e.area_name))

            grade_item = QTableWidgetItem(e.grade_label or "—")
            if e.grade_color:
                from PyQt6.QtGui import QColor
                grade_item.setBackground(QColor(e.grade_color))
                grade_item.setForeground(QColor("#FFFFFF"))
            self.eval_table.setItem(r, 2, grade_item)
            self.eval_table.setItem(r, 3, QTableWidgetItem(e.observations or ""))

        self.eval_table.resizeColumnsToContents()
        self.eval_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    def load_observations(self, observations: list[StudentObservation]):
        if not observations:
            self.obs_area.setPlainText("Sin observaciones registradas.")
            return
        lines = []
        for o in observations:
            lines.append(f"[{o.created_at[:10]}] {o.content}")
        self.obs_area.setPlainText("\n\n".join(lines))
