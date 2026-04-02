"""Ventana principal con sidebar y contenido apilado."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QStatusBar,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.views.components.sidebar import Sidebar
from mi_kinder.views.dashboard_view import DashboardView
from mi_kinder.theme.colors import *


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, is_directora: bool = False):
        super().__init__()
        self.setWindowTitle("Mi Kinder - Sistema de Gestion Escolar")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._sections: dict[str, QWidget] = {}
        self._setup_ui(is_directora)

    def _setup_ui(self, is_directora: bool):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(is_directora)
        self.sidebar.section_changed.connect(self._on_section_changed)
        self.sidebar.logout_btn.clicked.connect(self.logout_requested.emit)
        main_layout.addWidget(self.sidebar)

        # Contenido
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {BG_MAIN};")
        main_layout.addWidget(self.stack)

        # Dashboard siempre presente
        self.dashboard = DashboardView()
        self.add_section("dashboard", self.dashboard)

        # Placeholder para secciones no implementadas
        for section in ["groups", "students", "evaluations", "reports",
                        "charts", "attendance", "settings", "users"]:
            if section not in self._sections:
                placeholder = self._create_placeholder(section)
                self.add_section(section, placeholder)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {BG_CARD};
                border-top: 1px solid {BORDER};
                color: {TEXT_SECONDARY};
                font-size: 12px;
                padding: 3px 10px;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Mi Kinder v1.0.0")

        # Seleccionar dashboard por defecto
        self.sidebar.select_section("dashboard")

    def _create_placeholder(self, section: str) -> QWidget:
        names = {
            "groups": "Grupos",
            "students": "Alumnos",
            "evaluations": "Evaluaciones",
            "reports": "Reportes",
            "charts": "Graficas",
            "attendance": "Asistencia",
            "settings": "Ajustes",
            "users": "Usuarios",
        }
        widget = QWidget()
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(f"Seccion: {names.get(section, section)}\n\nProximamente...")
        label.setFont(QFont("Segoe UI", 18))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(label)
        return widget

    def add_section(self, name: str, widget: QWidget):
        if name in self._sections:
            idx = self.stack.indexOf(self._sections[name])
            self.stack.removeWidget(self._sections[name])
        self._sections[name] = widget
        self.stack.addWidget(widget)

    def _on_section_changed(self, section: str):
        widget = self._sections.get(section)
        if widget:
            self.stack.setCurrentWidget(widget)

    def set_status(self, message: str):
        self.status_bar.showMessage(message)
