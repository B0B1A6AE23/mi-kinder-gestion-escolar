"""Pantalla de inicio de sesion."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.theme.colors import *


class LoginView(QWidget):
    login_requested = pyqtSignal(str, str)  # username, password

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {PRIMARY_LIGHT};")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card central
        card = QFrame()
        card.setFixedSize(420, 480)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 20px;
                border: none;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        # Logo / Icono
        logo_label = QLabel("🏫")
        logo_label.setFont(QFont("Segoe UI Emoji", 48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        card_layout.addWidget(logo_label)

        # Titulo
        title = QLabel("Mi Kinder")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {PRIMARY_DARK}; background: transparent;")
        card_layout.addWidget(title)

        # Subtitulo
        subtitle = QLabel("Sistema de Gestion Escolar")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px; background: transparent;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(15)

        # Campo usuario
        user_label = QLabel("Usuario")
        user_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 13px; background: transparent;")
        card_layout.addWidget(user_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Ingresa tu usuario")
        self.username_input.setMinimumHeight(42)
        card_layout.addWidget(self.username_input)

        # Campo password
        pass_label = QLabel("Contrasena")
        pass_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 13px; background: transparent;")
        card_layout.addWidget(pass_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingresa tu contrasena")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.returnPressed.connect(self._on_login)
        card_layout.addWidget(self.password_input)

        card_layout.addSpacing(10)

        # Boton login
        self.login_btn = QPushButton("Iniciar Sesion")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
        """)
        self.login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(self.login_btn)

        # Mensaje error
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet(f"color: {ERROR}; font-size: 12px; background: transparent;")
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        card_layout.addStretch()

        layout.addWidget(card)

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.show_error("Ingresa usuario y contrasena")
            return
        self.login_requested.emit(username, password)

    def show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()

    def clear(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
        self.username_input.setFocus()
