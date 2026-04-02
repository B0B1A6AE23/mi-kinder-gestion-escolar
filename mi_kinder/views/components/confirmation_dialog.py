"""Dialogo de confirmacion reutilizable."""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


def confirm(parent, title: str, message: str) -> bool:
    dlg = QMessageBox(parent)
    dlg.setWindowTitle(title)
    dlg.setText(message)
    dlg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    dlg.setDefaultButton(QMessageBox.StandardButton.No)
    dlg.button(QMessageBox.StandardButton.Yes).setText("Si")
    dlg.button(QMessageBox.StandardButton.No).setText("No")
    return dlg.exec() == QMessageBox.StandardButton.Yes


def alert(parent, title: str, message: str):
    QMessageBox.warning(parent, title, message)


def info(parent, title: str, message: str):
    QMessageBox.information(parent, title, message)
