"""Sidebar de navegacion principal."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.theme.colors import *


class SidebarButton(QPushButton):
    """Boton del sidebar con estilo personalizado."""

    def __init__(self, icon: str, text: str, section: str):
        super().__init__(f"  {icon}  {text}")
        self.section = section
        self.setFixedHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 13))
        self._set_inactive()

    def _set_inactive(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0,0,0,0);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 15px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,0,0,0.15);
            }}
        """)

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SIDEBAR_ACTIVE};
                    color: {TEXT_LIGHT};
                    border: none;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 15px;
                    font-weight: bold;
                    font-size: 13px;
                }}
            """)
        else:
            self._set_inactive()


class Sidebar(QFrame):
    section_changed = pyqtSignal(str)

    def __init__(self, is_directora: bool = False):
        super().__init__()
        self.buttons: list[SidebarButton] = []
        self._setup_ui(is_directora)

    def _setup_ui(self, is_directora: bool):
        self.setFixedWidth(220)
        # QFrame pinta su fondo correctamente en PyQt6
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SIDEBAR};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # Logo
        logo = QLabel("🏫 Mi Kinder")
        logo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent; padding: 10px;")
        layout.addWidget(logo)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: rgba(255,255,255,0.4); border: none;")
        layout.addWidget(sep)
        layout.addSpacing(10)

        # Secciones principales
        sections = [
            ("🏠", "Inicio", "dashboard"),
            ("👥", "Grupos", "groups"),
            ("🧒", "Alumnos", "students"),
            ("📝", "Evaluaciones", "evaluations"),
            ("📊", "Reportes", "reports"),
            ("📈", "Graficas", "charts"),
            ("📋", "Asistencia", "attendance"),
        ]

        for icon, text, section in sections:
            btn = SidebarButton(icon, text, section)
            btn.clicked.connect(lambda checked, s=section: self._on_click(s))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # Secciones admin (solo directora)
        if is_directora:
            sep2 = QFrame()
            sep2.setFrameShape(QFrame.Shape.HLine)
            sep2.setFixedHeight(1)
            sep2.setStyleSheet("background-color: rgba(255,255,255,0.4); border: none;")
            layout.addWidget(sep2)
            layout.addSpacing(5)

            admin_sections = [
                ("⚙️", "Ajustes", "settings"),
                ("👤", "Usuarios", "users"),
            ]
            for icon, text, section in admin_sections:
                btn = SidebarButton(icon, text, section)
                btn.clicked.connect(lambda checked, s=section: self._on_click(s))
                layout.addWidget(btn)
                self.buttons.append(btn)

        # Boton cerrar sesion
        layout.addSpacing(10)
        self.logout_btn = QPushButton("  🚪  Cerrar Sesion")
        self.logout_btn.setFixedHeight(40)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {SECONDARY_LIGHT};
                border: 1px solid {SECONDARY_LIGHT};
                border-radius: 10px;
                text-align: left;
                padding-left: 15px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_DARK};
            }}
        """)
        layout.addWidget(self.logout_btn)

    def _on_click(self, section: str):
        for btn in self.buttons:
            btn.set_active(btn.section == section)
        self.section_changed.emit(section)

    def select_section(self, section: str):
        self._on_click(section)
