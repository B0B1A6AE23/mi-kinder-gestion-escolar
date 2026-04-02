"""Grid de captura de evaluaciones tipo hoja de calculo."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor
from mi_kinder.theme.colors import *


class EvaluationGridView(QWidget):
    save_requested = pyqtSignal(list)  # list of dicts
    group_changed = pyqtSignal(int)
    period_changed = pyqtSignal(int)
    export_excel_requested = pyqtSignal()

    def __init__(self, can_edit: bool = True):
        super().__init__()
        self._can_edit = can_edit
        self._areas = []
        self._students = []
        self._scale_levels = []
        self._current_evals = {}  # (student_id, area_id) -> eval data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Captura de Evaluaciones")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        # Selectores grupo + periodo
        selector_frame = QFrame()
        selector_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        sel_layout = QHBoxLayout(selector_frame)
        sel_layout.setContentsMargins(16, 12, 16, 12)
        sel_layout.setSpacing(16)

        grp_label = QLabel("Grupo:")
        grp_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 13px; background: transparent;")
        sel_layout.addWidget(grp_label)
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(200)
        self.group_combo.setMinimumHeight(36)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        sel_layout.addWidget(self.group_combo)

        per_label = QLabel("Periodo:")
        per_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; font-size: 13px; background: transparent;")
        sel_layout.addWidget(per_label)
        self.period_combo = QComboBox()
        self.period_combo.setMinimumWidth(200)
        self.period_combo.setMinimumHeight(36)
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        sel_layout.addWidget(self.period_combo)

        sel_layout.addStretch()

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        sel_layout.addWidget(self.progress_label)
        layout.addWidget(selector_frame)

        # Tabla
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                gridline-color: {BORDER};
                alternate-background-color: {BG_INPUT};
            }}
            QTableWidget::item {{ padding: 4px; }}
            QHeaderView::section {{
                background-color: {PRIMARY};
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 6px;
                border: none;
            }}
        """)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Barra de botones inferior
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        if self._can_edit:
            self.save_btn = QPushButton("💾 Guardar Todo")
            self.save_btn.setFixedHeight(42)
            self.save_btn.setMinimumWidth(180)
            self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.save_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0 20px;
                }}
                QPushButton:hover {{ background-color: #4CAF50; }}
            """)
            self.save_btn.clicked.connect(self._on_save)
            btn_bar.addWidget(self.save_btn)

        export_btn = QPushButton("📊 Exportar Excel")
        export_btn.setFixedHeight(42)
        export_btn.setMinimumWidth(160)
        export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {PRIMARY};
                border: 2px solid {PRIMARY};
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
        """)
        export_btn.clicked.connect(self.export_excel_requested.emit)
        btn_bar.addWidget(export_btn)

        btn_bar.addStretch()
        layout.addLayout(btn_bar)

    def load_groups(self, groups):
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItem("— Selecciona grupo —", None)
        for g in groups:
            self.group_combo.addItem(g.name, g.id)
        self.group_combo.blockSignals(False)

    def load_periods(self, periods):
        self.period_combo.blockSignals(True)
        self.period_combo.clear()
        self.period_combo.addItem("— Selecciona periodo —", None)
        for p in periods:
            self.period_combo.addItem(p.name, p.id)
        self.period_combo.blockSignals(False)

    def setup_grid(self, students, areas, scale_levels, evaluations):
        self._students = students
        self._areas = areas
        self._scale_levels = scale_levels
        self._current_evals = {}
        for e in evaluations:
            self._current_evals[(e.student_id, e.evaluation_area_id)] = e

        self.table.clear()
        self.table.setRowCount(len(students))
        self.table.setColumnCount(len(areas) + 1)

        headers = ["Alumno"] + [a.name for a in areas]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for c in range(1, len(areas) + 1):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)

        level_labels = ["—"] + [l.label for l in scale_levels]
        level_colors = {"—": None}
        level_ids = {"—": None}
        level_values = {"—": None}
        for l in scale_levels:
            level_colors[l.label] = l.color
            level_ids[l.label] = l.id
            level_values[l.label] = l.numeric_value

        evaluated_count = 0
        total_cells = len(students) * len(areas)

        for r, student in enumerate(students):
            name_item = QTableWidgetItem(student.full_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(r, 0, name_item)

            for c, area in enumerate(areas):
                combo = QComboBox()
                combo.addItems(level_labels)
                combo.setMinimumHeight(30)

                existing = self._current_evals.get((student.id, area.id))
                if existing and existing.grade_label:
                    idx = combo.findText(existing.grade_label)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                        evaluated_count += 1

                combo.setProperty("student_id", student.id)
                combo.setProperty("area_id", area.id)
                combo.currentTextChanged.connect(
                    lambda text, cb=combo: self._on_cell_changed(cb, text)
                )
                self._apply_combo_color(combo, combo.currentText(), level_colors)
                self.table.setCellWidget(r, c + 1, combo)

        self.table.setRowHeight(0, 38)
        for r in range(len(students)):
            self.table.setRowHeight(r, 38)

        if total_cells > 0:
            pct = evaluated_count * 100 // total_cells
            self.progress_label.setText(
                f"{evaluated_count} de {total_cells} evaluados ({pct}%)"
            )
        else:
            self.progress_label.setText("")

    def _apply_combo_color(self, combo, text, level_colors):
        color = level_colors.get(text)
        if color:
            combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    border-radius: 4px;
                    padding: 2px 6px;
                }}
            """)
        else:
            combo.setStyleSheet("")

    def _on_cell_changed(self, combo, text):
        level_colors = {l.label: l.color for l in self._scale_levels}
        level_colors["—"] = None
        self._apply_combo_color(combo, text, level_colors)

    def _on_group_changed(self, index):
        gid = self.group_combo.currentData()
        if gid is not None:
            self.group_changed.emit(gid)

    def _on_period_changed(self, index):
        pid = self.period_combo.currentData()
        if pid is not None:
            self.period_changed.emit(pid)

    def _on_save(self):
        results = []
        level_map = {l.label: l for l in self._scale_levels}
        for r in range(self.table.rowCount()):
            for c in range(1, self.table.columnCount()):
                combo = self.table.cellWidget(r, c)
                if not combo:
                    continue
                text = combo.currentText()
                if text == "—":
                    continue
                level = level_map.get(text)
                if not level:
                    continue
                results.append({
                    "student_id": combo.property("student_id"),
                    "area_id": combo.property("area_id"),
                    "grade_level_id": level.id,
                    "numeric_value": level.numeric_value,
                })
        self.save_requested.emit(results)

    def show_saved(self, count: int):
        self.progress_label.setText(f"✅ {count} evaluaciones guardadas")
