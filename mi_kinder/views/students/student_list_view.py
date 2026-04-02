"""Vista de lista de alumnos con filtro por grupo."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon
from mi_kinder.models.student import Student
from mi_kinder.models.group import Group
from mi_kinder.views.components.data_table import DataTable
from mi_kinder.theme.colors import *
import os


class StudentListView(QWidget):
    new_student_requested = pyqtSignal()
    edit_student_requested = pyqtSignal(int)
    view_student_requested = pyqtSignal(int)
    delete_student_requested = pyqtSignal(int)
    group_changed = pyqtSignal(int)   # group_id seleccionado

    def __init__(self, can_edit: bool = True):
        super().__init__()
        self._can_edit = can_edit
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # Titulo
        self.title_label = QLabel("Alumnos")
        self.title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(self.title_label)

        # Fila de acciones: filtro + contador + boton
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        filter_lbl = QLabel("Grupo:")
        filter_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        action_row.addWidget(filter_lbl)

        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(200)
        self.group_combo.setFixedHeight(36)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        action_row.addWidget(self.group_combo)

        self.count_label = QLabel("0 alumnos")
        self.count_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        action_row.addWidget(self.count_label)

        action_row.addStretch()

        if self._can_edit:
            self.new_btn = QPushButton("+ Nuevo Alumno")
            self.new_btn.setFixedHeight(40)
            self.new_btn.setMinimumWidth(160)
            self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.new_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0 16px;
                }}
                QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
            """)
            self.new_btn.clicked.connect(self.new_student_requested.emit)
            action_row.addWidget(self.new_btn)

        layout.addLayout(action_row)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["", "Nombre", "Grupo", "Tutor", "Telefono", "Acciones"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setColumnWidth(0, 50)   # foto
        self.table.setColumnWidth(5, 130)  # acciones
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                alternate-background-color: {BG_INPUT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                font-size: 13px;
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                padding: 4px 8px;
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item:selected {{
                background-color: {PRIMARY_LIGHT};
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {PRIMARY};
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)
        self.table.verticalHeader().setDefaultSectionSize(52)
        layout.addWidget(self.table)

    def load_groups(self, groups: list[Group]):
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItem("Todos los grupos", -1)
        for g in groups:
            self.group_combo.addItem(f"{g.name}  ({g.student_count})", g.id)
        self.group_combo.blockSignals(False)

    def load_students(self, students: list[Student]):
        self.table.setRowCount(0)
        self.count_label.setText(f"{len(students)} alumnos")
        self.table.setRowCount(len(students))

        for r, s in enumerate(students):
            self.table.setRowHeight(r, 52)

            # Foto (emoji si no hay)
            photo_lbl = QLabel("🧒")
            photo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_lbl.setStyleSheet("font-size: 24px; background: transparent;")
            if s.photo_path:
                from mi_kinder.config import get_photos_dir
                full = os.path.join(get_photos_dir(), s.photo_path)
                if os.path.exists(full):
                    pix = QPixmap(full).scaled(40, 40,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation)
                    photo_lbl.setPixmap(pix)
                    photo_lbl.setText("")
            self.table.setCellWidget(r, 0, photo_lbl)

            # Nombre
            name_item = QTableWidgetItem(s.full_name)
            name_item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.table.setItem(r, 1, name_item)

            self.table.setItem(r, 2, QTableWidgetItem(s.group_name))
            self.table.setItem(r, 3, QTableWidgetItem(s.guardian_name or ""))
            self.table.setItem(r, 4, QTableWidgetItem(s.guardian_phone or ""))

            # Botones de acciones
            actions = QWidget()
            actions.setStyleSheet("background: transparent;")
            act_layout = QHBoxLayout(actions)
            act_layout.setContentsMargins(4, 4, 4, 4)
            act_layout.setSpacing(4)

            view_btn = QPushButton("👁")
            view_btn.setFixedSize(28, 28)
            view_btn.setToolTip("Ver ficha")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet(f"""
                QPushButton {{ background-color: {INFO}; color: white;
                    border: none; border-radius: 5px; font-size: 13px; }}
                QPushButton:hover {{ background-color: #1565C0; }}
            """)
            view_btn.clicked.connect(lambda _, sid=s.id: self.view_student_requested.emit(sid))
            act_layout.addWidget(view_btn)

            if self._can_edit:
                edit_btn = QPushButton("✏️")
                edit_btn.setFixedSize(28, 28)
                edit_btn.setToolTip("Editar")
                edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                edit_btn.setStyleSheet(f"""
                    QPushButton {{ background-color: {SECONDARY}; color: white;
                        border: none; border-radius: 5px; font-size: 13px; }}
                    QPushButton:hover {{ background-color: {PRIMARY}; }}
                """)
                edit_btn.clicked.connect(lambda _, sid=s.id: self.edit_student_requested.emit(sid))
                act_layout.addWidget(edit_btn)

                del_btn = QPushButton("🗑")
                del_btn.setFixedSize(28, 28)
                del_btn.setToolTip("Dar de baja")
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.setStyleSheet(f"""
                    QPushButton {{ background-color: {ERROR}; color: white;
                        border: none; border-radius: 5px; font-size: 13px; }}
                    QPushButton:hover {{ background-color: #B71C1C; }}
                """)
                del_btn.clicked.connect(lambda _, sid=s.id: self.delete_student_requested.emit(sid))
                act_layout.addWidget(del_btn)

            self.table.setCellWidget(r, 5, actions)

    def _on_group_changed(self):
        gid = self.group_combo.currentData()
        if gid is not None:
            self.group_changed.emit(gid)

    def get_selected_group_id(self) -> int:
        return self.group_combo.currentData() or -1
