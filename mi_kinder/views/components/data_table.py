"""Tabla reutilizable con busqueda y acciones."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QLabel,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.theme.colors import *


class DataTable(QWidget):
    """Tabla generica con barra de busqueda opcional."""
    row_double_clicked = pyqtSignal(int)  # row index

    def __init__(self, columns: list[str], searchable: bool = True):
        super().__init__()
        self._columns = columns
        self._setup_ui(searchable)

    def _setup_ui(self, searchable: bool):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if searchable:
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("🔍  Buscar...")
            self.search_input.setMinimumHeight(38)
            self.search_input.textChanged.connect(self._filter)
            layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self._columns))
        self.table.setHorizontalHeaderLabels(self._columns)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: {BG_INPUT};
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 8px;
                gridline-color: {BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {PRIMARY_LIGHT};
                color: {TEXT_PRIMARY};
            }}
        """)
        self.table.doubleClicked.connect(
            lambda idx: self.row_double_clicked.emit(idx.row())
        )
        layout.addWidget(self.table)

    def set_data(self, rows: list[list[str]]):
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def set_row_data(self, row: int, key: str, value):
        """Guarda un dato extra en la primera celda de la fila (UserRole)."""
        item = self.table.item(row, 0)
        if item:
            item.setData(Qt.ItemDataRole.UserRole, value)

    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _filter(self, text: str):
        text = text.lower()
        for r in range(self.table.rowCount()):
            match = any(
                text in (self.table.item(r, c).text().lower() if self.table.item(r, c) else "")
                for c in range(self.table.columnCount())
            )
            self.table.setRowHidden(r, not match)
