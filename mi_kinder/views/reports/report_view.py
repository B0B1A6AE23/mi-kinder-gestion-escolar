"""Vista de reportes con tabs: Individual, Grupal, General."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTabWidget, QFrame, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.theme.colors import *


def _styled_primary_btn(text: str, min_w: int = 180) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(42)
    btn.setMinimumWidth(min_w)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            padding: 0 18px;
        }}
        QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
    """)
    return btn


class ReportView(QWidget):
    generate_individual = pyqtSignal(int)   # student_id
    generate_group = pyqtSignal(int)        # group_id
    generate_general = pyqtSignal()
    generate_boletas = pyqtSignal(int)      # group_id

    def __init__(self, is_directora: bool = False):
        super().__init__()
        self._is_directora = is_directora
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Reportes")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_individual_tab(), "🧒 Individual")
        self.tabs.addTab(self._build_group_tab(), "👥 Grupal")
        if self._is_directora:
            self.tabs.addTab(self._build_general_tab(), "🏫 General")
        self.tabs.addTab(self._build_boleta_tab(), "📄 Boletas")
        layout.addWidget(self.tabs)

    def _build_individual_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)
        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl)
        self.ind_group_combo = QComboBox()
        self.ind_group_combo.setMinimumWidth(200)
        self.ind_group_combo.setMinimumHeight(36)
        self.ind_group_combo.currentIndexChanged.connect(self._on_ind_group_changed)
        sel_row.addWidget(self.ind_group_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        self.student_list = QListWidget()
        self.student_list.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {BORDER}; border-radius: 8px; background: {BG_CARD}; }}
            QListWidget::item {{ padding: 8px; border-bottom: 1px solid {BORDER}; }}
            QListWidget::item:selected {{ background-color: {PRIMARY_LIGHT}; }}
        """)
        layout.addWidget(self.student_list)

        gen_btn = _styled_primary_btn("📄 Generar Reporte Individual")
        gen_btn.clicked.connect(self._on_gen_individual)
        layout.addWidget(gen_btn)
        return w

    def _build_group_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        sel_row = QHBoxLayout()
        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl)
        self.grp_group_combo = QComboBox()
        self.grp_group_combo.setMinimumWidth(200)
        self.grp_group_combo.setMinimumHeight(36)
        sel_row.addWidget(self.grp_group_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        layout.addStretch()

        gen_btn = _styled_primary_btn("📊 Generar Reporte Grupal")
        gen_btn.clicked.connect(self._on_gen_group)
        layout.addWidget(gen_btn)
        return w

    def _build_general_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        info_lbl = QLabel(
            "El reporte general compara todos los grupos del ciclo activo.\n"
            "Incluye promedios por area y ranking de grupos."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(info_lbl)

        layout.addStretch()

        gen_btn = _styled_primary_btn("🏫 Generar Reporte General")
        gen_btn.clicked.connect(self.generate_general.emit)
        layout.addWidget(gen_btn)
        return w

    def _build_boleta_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        sel_row = QHBoxLayout()
        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_row.addWidget(lbl)
        self.bol_group_combo = QComboBox()
        self.bol_group_combo.setMinimumWidth(200)
        self.bol_group_combo.setMinimumHeight(36)
        sel_row.addWidget(self.bol_group_combo)
        sel_row.addStretch()
        layout.addLayout(sel_row)

        info_lbl = QLabel("Genera boletas de calificaciones para todos los alumnos del grupo.")
        info_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(info_lbl)

        layout.addStretch()

        gen_btn = _styled_primary_btn("📄 Generar Boletas del Grupo")
        gen_btn.clicked.connect(self._on_gen_boletas)
        layout.addWidget(gen_btn)
        return w

    def load_groups(self, groups):
        for combo in [self.ind_group_combo, self.grp_group_combo, self.bol_group_combo]:
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("— Selecciona grupo —", None)
            for g in groups:
                combo.addItem(g.name, g.id)
            combo.blockSignals(False)

    def load_students(self, students):
        self.student_list.clear()
        for s in students:
            item = QListWidgetItem(f"{s.full_name}  —  {s.group_name}")
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.student_list.addItem(item)

    def _on_ind_group_changed(self, index):
        gid = self.ind_group_combo.currentData()
        if gid:
            from mi_kinder.services.session import Session
            # Signal handled by presenter
            pass

    def _on_gen_individual(self):
        item = self.student_list.currentItem()
        if item:
            self.generate_individual.emit(item.data(Qt.ItemDataRole.UserRole))

    def _on_gen_group(self):
        gid = self.grp_group_combo.currentData()
        if gid:
            self.generate_group.emit(gid)

    def _on_gen_boletas(self):
        gid = self.bol_group_combo.currentData()
        if gid:
            self.generate_boletas.emit(gid)
