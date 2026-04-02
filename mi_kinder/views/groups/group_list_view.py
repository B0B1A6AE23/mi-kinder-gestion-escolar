"""Vista de lista de grupos."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.models.group import Group
from mi_kinder.theme.colors import *


class GroupCard(QFrame):
    edit_clicked = pyqtSignal(int)
    view_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)

    def __init__(self, group: Group, can_edit: bool = True):
        super().__init__()
        self._group = group
        self._setup_ui(can_edit)

    def _setup_ui(self, can_edit: bool):
        self.setFixedHeight(140)
        self.setMinimumWidth(240)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
            QFrame:hover {{
                border: 2px solid {PRIMARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Nombre del grupo
        name_lbl = QLabel(self._group.name)
        name_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {PRIMARY_DARK}; background: transparent;")
        layout.addWidget(name_lbl)

        # Info
        teacher = self._group.teacher_name or "Sin maestra asignada"
        count = self._group.student_count
        info_lbl = QLabel(f"👩‍🏫 {teacher}\n🧒 {count} alumnos")
        info_lbl.setFont(QFont("Segoe UI", 11))
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(info_lbl)

        layout.addStretch()

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        view_btn = QPushButton("Ver alumnos")
        view_btn.setFixedHeight(30)
        view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        view_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
        """)
        view_btn.clicked.connect(lambda: self.view_clicked.emit(self._group.id))
        btn_row.addWidget(view_btn)

        if can_edit:
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setToolTip("Editar")
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SECONDARY};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: {PRIMARY}; }}
            """)
            edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self._group.id))
            btn_row.addWidget(edit_btn)

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setToolTip("Eliminar")
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ERROR};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: #B71C1C; }}
            """)
            del_btn.clicked.connect(lambda: self.delete_clicked.emit(self._group.id))
            btn_row.addWidget(del_btn)

        layout.addLayout(btn_row)


class GroupListView(QWidget):
    new_group_requested = pyqtSignal()
    edit_group_requested = pyqtSignal(int)
    view_group_requested = pyqtSignal(int)
    delete_group_requested = pyqtSignal(int)

    def __init__(self, can_edit: bool = True):
        super().__init__()
        self._can_edit = can_edit
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        # Titulo
        title = QLabel("Grupos")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        # Fila de acciones: contador + boton
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.count_label = QLabel("0 grupos")
        self.count_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        action_row.addWidget(self.count_label)
        action_row.addStretch()

        if self._can_edit:
            self.new_btn = QPushButton("+ Nuevo Grupo")
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
            self.new_btn.clicked.connect(self.new_group_requested.emit)
            action_row.addWidget(self.new_btn)

        layout.addLayout(action_row)

        # Area de scroll con grid de cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self._grid_widget)
        layout.addWidget(scroll)

    def load_groups(self, groups: list[Group]):
        # Limpiar grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.count_label.setText(f"{len(groups)} grupos")

        cols = 3
        for i, group in enumerate(groups):
            card = GroupCard(group, self._can_edit)
            card.edit_clicked.connect(self.edit_group_requested.emit)
            card.view_clicked.connect(self.view_group_requested.emit)
            card.delete_clicked.connect(self.delete_group_requested.emit)
            self._grid.addWidget(card, i // cols, i % cols)

        if not groups:
            empty = QLabel("No hay grupos creados.\nHaz clic en '+ Nuevo Grupo' para comenzar.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 15px;")
            self._grid.addWidget(empty, 0, 0, 1, cols)
