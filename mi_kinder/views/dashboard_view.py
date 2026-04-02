"""Vista del dashboard principal."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.views.components.stat_card import StatCard
from mi_kinder.theme.colors import *


class DashboardView(QWidget):
    navigate_to = pyqtSignal(str)  # section name

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Titulo
        title = QLabel("Panel Principal")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        self.welcome_label = QLabel("Bienvenida")
        self.welcome_label.setFont(QFont("Segoe UI", 14))
        self.welcome_label.setStyleSheet(f"color: {TEXT_SECONDARY};")
        layout.addWidget(self.welcome_label)

        # Stat cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.card_students = StatCard("🧒", "Alumnos", "0", PRIMARY)
        self.card_groups = StatCard("👥", "Grupos", "0", SECONDARY)
        self.card_teachers = StatCard("👩‍🏫", "Maestras", "0", ACCENT)
        self.card_attendance = StatCard("📋", "Asistencia", "0%", SUCCESS)

        cards_layout.addWidget(self.card_students)
        cards_layout.addWidget(self.card_groups)
        cards_layout.addWidget(self.card_teachers)
        cards_layout.addWidget(self.card_attendance)
        layout.addLayout(cards_layout)

        # Accesos rapidos
        quick_frame = QFrame()
        quick_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 15px;
                border: 1px solid {BORDER};
            }}
        """)
        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setContentsMargins(20, 15, 20, 15)

        quick_title = QLabel("Accesos Rapidos")
        quick_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        quick_title.setStyleSheet(f"color: {PRIMARY_DARK};")
        quick_layout.addWidget(quick_title)

        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(10)

        quick_actions = [
            ("📝 Capturar Evaluaciones", "evaluations"),
            ("🧒 Nuevo Alumno", "students"),
            ("📊 Ver Reportes", "reports"),
            ("📈 Ver Graficas", "charts"),
        ]

        for text, section in quick_actions:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BG_CARD};
                    color: {PRIMARY};
                    border: 2px solid {PRIMARY};
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 8px 14px;
                }}
                QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
            """)
            btn.clicked.connect(lambda checked, s=section: self.navigate_to.emit(s))
            btns_layout.addWidget(btn)

        quick_layout.addLayout(btns_layout)
        layout.addWidget(quick_frame)

        layout.addStretch()

    def update_stats(self, students: int, groups: int, teachers: int, attendance: float):
        self.card_students.set_value(str(students))
        self.card_groups.set_value(str(groups))
        self.card_teachers.set_value(str(teachers))
        self.card_attendance.set_value(f"{attendance:.0f}%")

    def set_welcome(self, name: str):
        self.welcome_label.setText(f"Bienvenida, {name}")
