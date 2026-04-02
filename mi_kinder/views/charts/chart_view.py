"""Vista de graficas con matplotlib embebido en PyQt6."""
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from mi_kinder.theme.colors import *

# Colores matplotlib (convertir hex a 0-1)
CHART_COLORS = ["#FF7043", "#FFB74D", "#7E57C2", "#66BB6A", "#42A5F5",
                "#EF5350", "#FFA726", "#26C6DA", "#AB47BC", "#8D6E63"]


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


class ChartCanvas(FigureCanvas):
    def __init__(self, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor("#FFF8F0")
        super().__init__(self.fig)

    def clear(self):
        self.fig.clear()
        self.draw()


class ChartView(QWidget):
    # Individual
    ind_group_changed = pyqtSignal(int)
    ind_student_selected = pyqtSignal(int)
    ind_period_selected = pyqtSignal(int)
    # Grupal
    grp_group_changed = pyqtSignal(int)
    grp_period_changed = pyqtSignal(int)
    # General
    gen_requested = pyqtSignal()
    # Export
    export_requested = pyqtSignal(str)  # "png"

    def __init__(self, is_directora: bool = False):
        super().__init__()
        self._is_directora = is_directora
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Graficas")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_individual_tab(), "🧒 Individual")
        self.tabs.addTab(self._build_group_tab(), "👥 Grupal")
        if self._is_directora:
            self.tabs.addTab(self._build_general_tab(), "🏫 General")
        layout.addWidget(self.tabs)

    def _build_individual_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)
        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl)
        self.ind_group_combo = QComboBox()
        self.ind_group_combo.setMinimumWidth(180)
        self.ind_group_combo.setMinimumHeight(34)
        self.ind_group_combo.currentIndexChanged.connect(
            lambda: self._emit_combo(self.ind_group_combo, self.ind_group_changed)
        )
        sel_row.addWidget(self.ind_group_combo)

        lbl2 = QLabel("Alumno:")
        lbl2.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl2)
        self.ind_student_combo = QComboBox()
        self.ind_student_combo.setMinimumWidth(220)
        self.ind_student_combo.setMinimumHeight(34)
        sel_row.addWidget(self.ind_student_combo)

        gen_btn = _styled_primary_btn("📈 Generar", 120)
        gen_btn.clicked.connect(
            lambda: self._emit_combo(self.ind_student_combo, self.ind_student_selected)
        )
        sel_row.addWidget(gen_btn)
        sel_row.addStretch()

        save_btn = _styled_primary_btn("💾 Guardar PNG", 130)
        save_btn.clicked.connect(lambda: self.export_requested.emit("png"))
        sel_row.addWidget(save_btn)
        layout.addLayout(sel_row)

        self.ind_canvas = ChartCanvas(9, 5)
        layout.addWidget(self.ind_canvas)
        return w

    def _build_group_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)
        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl)
        self.grp_group_combo = QComboBox()
        self.grp_group_combo.setMinimumWidth(180)
        self.grp_group_combo.setMinimumHeight(34)
        sel_row.addWidget(self.grp_group_combo)

        lbl2 = QLabel("Periodo:")
        lbl2.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl2)
        self.grp_period_combo = QComboBox()
        self.grp_period_combo.setMinimumWidth(180)
        self.grp_period_combo.setMinimumHeight(34)
        sel_row.addWidget(self.grp_period_combo)

        gen_btn = _styled_primary_btn("📊 Generar", 120)
        gen_btn.clicked.connect(self._on_grp_generate)
        sel_row.addWidget(gen_btn)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        self.grp_canvas = ChartCanvas(9, 5)
        layout.addWidget(self.grp_canvas)
        return w

    def _build_general_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        btn_row = QHBoxLayout()
        gen_btn = _styled_primary_btn("🏫 Generar Comparacion General", 260)
        gen_btn.clicked.connect(self.gen_requested.emit)
        btn_row.addWidget(gen_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.gen_canvas = ChartCanvas(10, 6)
        layout.addWidget(self.gen_canvas)
        return w

    def _emit_combo(self, combo, signal):
        val = combo.currentData()
        if val is not None:
            signal.emit(val)

    def _on_grp_generate(self):
        gid = self.grp_group_combo.currentData()
        pid = self.grp_period_combo.currentData()
        if gid and pid:
            self.grp_group_changed.emit(gid)
            self.grp_period_changed.emit(pid)

    # ── Drawing Methods ──

    def load_groups(self, groups):
        for combo in [self.ind_group_combo, self.grp_group_combo]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("— Grupo —", None)
            for g in groups:
                combo.addItem(g.name, g.id)
            combo.blockSignals(False)

    def load_periods(self, periods):
        self.grp_period_combo.blockSignals(True)
        self.grp_period_combo.clear()
        self.grp_period_combo.addItem("— Periodo —", None)
        for p in periods:
            self.grp_period_combo.addItem(p.name, p.id)
        self.grp_period_combo.blockSignals(False)

    def load_students(self, students):
        self.ind_student_combo.blockSignals(True)
        self.ind_student_combo.clear()
        self.ind_student_combo.addItem("— Alumno —", None)
        for s in students:
            self.ind_student_combo.addItem(s.full_name, s.id)
        self.ind_student_combo.blockSignals(False)

    def draw_progress_line(self, period_names, series, student_name=""):
        self.ind_canvas.clear()
        ax = self.ind_canvas.fig.add_subplot(111)
        x = range(len(period_names))

        for i, (area_name, values) in enumerate(series.items()):
            clean = [v if v is not None else 0 for v in values]
            color = CHART_COLORS[i % len(CHART_COLORS)]
            ax.plot(x, clean, marker="o", label=area_name, color=color, linewidth=2)

        ax.set_xticks(list(x))
        ax.set_xticklabels(period_names)
        ax.set_ylabel("Calificacion")
        ax.set_title(f"Progreso de {student_name}" if student_name else "Progreso")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
        self.ind_canvas.fig.tight_layout()
        self.ind_canvas.draw()

    def draw_group_bars(self, area_names, averages, group_name=""):
        self.grp_canvas.clear()
        ax = self.grp_canvas.fig.add_subplot(111)
        x = range(len(area_names))
        colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in x]

        ax.bar(x, averages, color=colors)
        ax.set_xticks(list(x))
        ax.set_xticklabels(area_names, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("Promedio")
        ax.set_title(f"Promedios — {group_name}" if group_name else "Promedios Grupales")
        ax.grid(True, alpha=0.3, axis="y")
        self.grp_canvas.fig.tight_layout()
        self.grp_canvas.draw()

    def draw_group_distribution(self, area_names, level_labels, level_colors, data):
        self.grp_canvas.clear()
        ax = self.grp_canvas.fig.add_subplot(111)
        x = np.arange(len(area_names))
        width = 0.6
        bottom = np.zeros(len(area_names))

        for i, label in enumerate(level_labels):
            values = [data.get(a, {}).get(label, 0) for a in area_names]
            color = level_colors[i] if i < len(level_colors) else CHART_COLORS[i % len(CHART_COLORS)]
            ax.bar(x, values, width, bottom=bottom, label=label, color=color)
            bottom += np.array(values)

        ax.set_xticks(x)
        ax.set_xticklabels(area_names, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("Cantidad de alumnos")
        ax.set_title("Distribucion de Niveles por Area")
        ax.legend(loc="best", fontsize=8)
        self.grp_canvas.fig.tight_layout()
        self.grp_canvas.draw()

    def draw_general_heatmap(self, group_names, area_names, matrix):
        self.gen_canvas.clear()
        ax = self.gen_canvas.fig.add_subplot(111)

        arr = np.array(matrix, dtype=float)
        im = ax.imshow(arr, cmap="RdYlGn", aspect="auto", vmin=0, vmax=3)

        ax.set_xticks(range(len(area_names)))
        ax.set_xticklabels(area_names, rotation=35, ha="right", fontsize=8)
        ax.set_yticks(range(len(group_names)))
        ax.set_yticklabels(group_names, fontsize=9)
        ax.set_title("Comparacion General — Heatmap")
        self.gen_canvas.fig.colorbar(im, ax=ax, label="Promedio")

        for i in range(len(group_names)):
            for j in range(len(area_names)):
                val = arr[i, j]
                if val > 0:
                    ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=8,
                            color="white" if val < 1.5 else "black")

        self.gen_canvas.fig.tight_layout()
        self.gen_canvas.draw()
