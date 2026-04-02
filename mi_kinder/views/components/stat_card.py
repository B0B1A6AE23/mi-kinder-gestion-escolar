"""Widget de tarjeta estadistica para el dashboard."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from mi_kinder.theme.colors import BG_CARD, TEXT_LIGHT


class StatCard(QFrame):
    def __init__(self, icon: str, title: str, value: str, color: str):
        super().__init__()
        self.setFixedHeight(120)
        self.setMinimumWidth(180)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        # Icono + titulo
        header = QLabel(f"{icon} {title}")
        header.setFont(QFont("Segoe UI", 12))
        header.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent;")
        layout.addWidget(header)

        # Valor
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {TEXT_LIGHT}; background: transparent;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        self.value_label.setText(value)
