"""Vista de asistencia con grid diario."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QFont, QColor
from mi_kinder.theme.colors import *

STATUS_COLORS = {
    "present": ("#66BB6A", "A"),
    "absent": ("#EF5350", "F"),
    "late": ("#FFA726", "R"),
    "justified": ("#42A5F5", "J"),
}
STATUS_CYCLE = ["present", "absent", "late", "justified"]


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


class AttendanceView(QWidget):
    save_requested = pyqtSignal(list)  # list of dicts
    group_changed = pyqtSignal(int)
    date_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._students = []
        self._current_records = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Control de Asistencia")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        # Selectores
        sel_frame = QFrame()
        sel_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid {BORDER};
            }}
        """)
        sel_layout = QHBoxLayout(sel_frame)
        sel_layout.setContentsMargins(16, 12, 16, 12)
        sel_layout.setSpacing(12)

        lbl = QLabel("Grupo:")
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_layout.addWidget(lbl)
        self.group_combo = QComboBox()
        self.group_combo.setMinimumWidth(200)
        self.group_combo.setMinimumHeight(36)
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        sel_layout.addWidget(self.group_combo)

        lbl2 = QLabel("Fecha:")
        lbl2.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        sel_layout.addWidget(lbl2)
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumHeight(36)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        sel_layout.addWidget(self.date_edit)

        sel_layout.addStretch()

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        sel_layout.addWidget(self.stats_label)
        layout.addWidget(sel_frame)

        # Leyenda
        legend = QHBoxLayout()
        for status, (color, letter) in STATUS_COLORS.items():
            labels_map = {"present": "Asistio", "absent": "Falta", "late": "Retardo", "justified": "Justificado"}
            lbl = QLabel(f"  {letter} = {labels_map[status]}  ")
            lbl.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; font-weight: bold; padding: 2px 8px;")
            legend.addWidget(lbl)
        legend.addStretch()
        layout.addLayout(legend)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Alumno", "Estado", "Notas"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                alternate-background-color: {BG_INPUT};
                color: {TEXT_PRIMARY};
            }}
            QTableWidget::item {{ color: {TEXT_PRIMARY}; }}
            QHeaderView::section {{
                background-color: {PRIMARY};
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)
        layout.addWidget(self.table)

        save_btn = _styled_primary_btn("💾 Guardar Asistencia", 200)
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

    def load_groups(self, groups):
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItem("— Selecciona grupo —", None)
        for g in groups:
            self.group_combo.addItem(g.name, g.id)
        self.group_combo.blockSignals(False)

    def setup_grid(self, students, records):
        self._students = students
        self._current_records = {r.student_id: r for r in records}

        self.table.setRowCount(len(students))
        present_count = 0

        for r, s in enumerate(students):
            name_item = QTableWidgetItem(s.full_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, 0, name_item)

            existing = self._current_records.get(s.id)
            status = existing.status if existing else "present"

            status_btn = QPushButton()
            status_btn.setProperty("student_id", s.id)
            status_btn.setProperty("status", status)
            status_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._style_status_btn(status_btn, status)
            status_btn.clicked.connect(lambda _, btn=status_btn: self._toggle_status(btn))
            self.table.setCellWidget(r, 1, status_btn)

            notes_item = QTableWidgetItem(existing.notes if existing else "")
            self.table.setItem(r, 2, notes_item)

            self.table.setRowHeight(r, 38)

            if status == "present":
                present_count += 1

        total = len(students)
        pct = present_count * 100 // total if total > 0 else 0
        self.stats_label.setText(f"Presentes: {present_count}/{total} ({pct}%)")

    def _style_status_btn(self, btn, status):
        color, letter = STATUS_COLORS.get(status, ("#999", "?"))
        btn.setText(letter)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 6px;
                min-width: 40px;
                min-height: 30px;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)

    def _toggle_status(self, btn):
        current = btn.property("status")
        idx = STATUS_CYCLE.index(current) if current in STATUS_CYCLE else 0
        next_status = STATUS_CYCLE[(idx + 1) % len(STATUS_CYCLE)]
        btn.setProperty("status", next_status)
        self._style_status_btn(btn, next_status)
        self._update_stats()

    def _update_stats(self):
        present = 0
        total = self.table.rowCount()
        for r in range(total):
            btn = self.table.cellWidget(r, 1)
            if btn and btn.property("status") == "present":
                present += 1
        pct = present * 100 // total if total > 0 else 0
        self.stats_label.setText(f"Presentes: {present}/{total} ({pct}%)")

    def _on_group_changed(self, index):
        gid = self.group_combo.currentData()
        if gid:
            self.group_changed.emit(gid)

    def _on_date_changed(self, date):
        d = self.date_edit.date()
        self.date_changed.emit(f"{d.year()}-{d.month():02d}-{d.day():02d}")

    def _on_save(self):
        d = self.date_edit.date()
        date_str = f"{d.year()}-{d.month():02d}-{d.day():02d}"
        results = []
        for r in range(self.table.rowCount()):
            btn = self.table.cellWidget(r, 1)
            notes_item = self.table.item(r, 2)
            if btn:
                results.append({
                    "student_id": btn.property("student_id"),
                    "status": btn.property("status"),
                    "date": date_str,
                    "notes": notes_item.text() if notes_item else "",
                })
        self.save_requested.emit(results)

    def show_saved(self):
        self.stats_label.setText("✅ Asistencia guardada")

    def get_current_date_str(self) -> str:
        d = self.date_edit.date()
        return f"{d.year()}-{d.month():02d}-{d.day():02d}"
