"""Gestion de escalas de evaluacion (tab en Ajustes)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QColorDialog, QSpinBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from mi_kinder.models.evaluation import GradingScale, GradingScaleLevel
from mi_kinder.theme.colors import *


def _styled_primary_btn(text: str, min_w: int = 180) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(40)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            padding: 0 14px;
        }}
        QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
    """)
    return btn


def _styled_secondary_btn(text: str, min_w: int = 180) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(40)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {BG_CARD};
            color: {PRIMARY};
            border: 2px solid {PRIMARY};
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            padding: 0 14px;
        }}
        QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
    """)
    return btn


class ScaleDialog(QDialog):
    def __init__(self, parent=None, scale: GradingScale | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Escala" if not scale else "Editar Escala")
        self.setMinimumWidth(520)
        self.setMinimumHeight(450)
        self.setModal(True)
        self._scale = scale
        self._colors = {}
        self._setup_ui()
        if scale and scale.levels:
            self._load(scale)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ej: Logros de Aprendizaje")
        self.name_input.setMinimumHeight(36)
        form.addRow("Nombre *:", self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Etiqueta (Logrado/En Proceso)", "label")
        self.type_combo.addItem("Numerico (1-10)", "numeric")
        self.type_combo.addItem("Letra (A-E)", "letter")
        self.type_combo.setMinimumHeight(36)
        form.addRow("Tipo:", self.type_combo)

        layout.addLayout(form)

        levels_label = QLabel("Niveles de la escala:")
        levels_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        levels_label.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(levels_label)

        self.levels_table = QTableWidget()
        self.levels_table.setColumnCount(4)
        self.levels_table.setHorizontalHeaderLabels(["Etiqueta", "Valor", "Color", "Orden"])
        self.levels_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.levels_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.levels_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.levels_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.levels_table.setStyleSheet(f"border: 1px solid {BORDER};")
        layout.addWidget(self.levels_table)

        level_btns = QHBoxLayout()
        add_level_btn = _styled_secondary_btn("+ Agregar Nivel", 150)
        add_level_btn.clicked.connect(self._add_level_row)
        level_btns.addWidget(add_level_btn)

        rm_level_btn = _styled_secondary_btn("- Quitar Nivel", 150)
        rm_level_btn.clicked.connect(self._remove_level_row)
        level_btns.addWidget(rm_level_btn)
        level_btns.addStretch()
        layout.addLayout(level_btns)

        row = QHBoxLayout()
        row.addStretch()
        cancel = _styled_secondary_btn("Cancelar", 110)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)
        save = _styled_primary_btn("Guardar", 110)
        save.clicked.connect(self._validate)
        row.addWidget(save)
        layout.addLayout(row)

    def _add_level_row(self, label="", value=0.0, color="#66BB6A", order=None):
        r = self.levels_table.rowCount()
        self.levels_table.setRowCount(r + 1)

        self.levels_table.setItem(r, 0, QTableWidgetItem(label))

        val_item = QTableWidgetItem(str(value))
        self.levels_table.setItem(r, 1, val_item)

        color_btn = QPushButton()
        color_btn.setFixedSize(50, 28)
        self._colors[r] = color
        color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid {BORDER}; border-radius: 4px;")
        color_btn.clicked.connect(lambda _, row=r, btn=color_btn: self._pick_color(row, btn))
        self.levels_table.setCellWidget(r, 2, color_btn)

        ord_item = QTableWidgetItem(str(order if order is not None else r))
        self.levels_table.setItem(r, 3, ord_item)

    def _remove_level_row(self):
        r = self.levels_table.currentRow()
        if r >= 0:
            self.levels_table.removeRow(r)

    def _pick_color(self, row, btn):
        color = QColorDialog.getColor(QColor(self._colors.get(row, "#66BB6A")), self)
        if color.isValid():
            self._colors[row] = color.name()
            btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid {BORDER}; border-radius: 4px;")

    def _load(self, s: GradingScale):
        self.name_input.setText(s.name)
        idx = self.type_combo.findData(s.scale_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        for level in s.levels:
            self._add_level_row(level.label, level.numeric_value or 0, level.color or "#66BB6A", level.sort_order)

    def _validate(self):
        if not self.name_input.text().strip():
            self.name_input.setStyleSheet(f"border: 2px solid {ERROR};")
            return
        if self.levels_table.rowCount() == 0:
            return
        self.accept()

    def get_data(self) -> dict:
        levels = []
        for r in range(self.levels_table.rowCount()):
            label = self.levels_table.item(r, 0)
            value = self.levels_table.item(r, 1)
            order = self.levels_table.item(r, 3)
            levels.append({
                "label": label.text() if label else "",
                "numeric_value": float(value.text()) if value and value.text() else 0,
                "color": self._colors.get(r, "#66BB6A"),
                "sort_order": int(order.text()) if order and order.text() else r,
            })
        return {
            "name": self.name_input.text().strip(),
            "scale_type": self.type_combo.currentData(),
            "levels": levels,
        }


class ScaleManagementWidget(QWidget):
    scale_created = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._scales: list[GradingScale] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        info_lbl = QLabel("Escalas de evaluacion disponibles:")
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(info_lbl)

        btn_row = QHBoxLayout()
        new_btn = _styled_primary_btn("+ Nueva Escala", 160)
        new_btn.clicked.connect(self._on_new)
        btn_row.addWidget(new_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.scale_list = QListWidget()
        self.scale_list.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {BORDER}; border-radius: 8px; background: {BG_CARD}; color: {TEXT_PRIMARY}; }}
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid {BORDER}; color: {TEXT_PRIMARY}; }}
            QListWidget::item:selected {{ background-color: {PRIMARY_LIGHT}; color: {TEXT_PRIMARY}; }}
        """)
        layout.addWidget(self.scale_list)

    def load_scales(self, scales: list[GradingScale]):
        self._scales = scales
        self.scale_list.clear()
        for s in scales:
            default_tag = " ⭐ (Por defecto)" if s.is_default else ""
            levels_str = ", ".join(l.label for l in (s.levels or []))
            text = f"{s.name}{default_tag}\n   Niveles: {levels_str}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.scale_list.addItem(item)

    def _on_new(self):
        dlg = ScaleDialog(self)
        if dlg.exec():
            self.scale_created.emit(dlg.get_data())
