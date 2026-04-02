"""Vista de gestion de usuarios (maestras)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QCheckBox, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from mi_kinder.models.user import User
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


class UserFormDialog(QDialog):
    def __init__(self, parent=None, user: User | None = None, groups=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Maestra" if not user else "Editar Maestra")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._user = user
        self._groups = groups or []
        self._setup_ui()
        if user:
            self._load(user)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Nombre completo")
        self.full_name.setMinimumHeight(36)
        form.addRow("Nombre *:", self.full_name)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Usuario para login")
        self.username.setMinimumHeight(36)
        form.addRow("Usuario *:", self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Contrasena" if not self._user else "Dejar vacio para no cambiar")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setMinimumHeight(36)
        form.addRow("Contrasena:", self.password)

        self.active_check = QCheckBox("Activa")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)

        layout.addLayout(form)

        # Asignar grupos
        grp_lbl = QLabel("Asignar grupos:")
        grp_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        grp_lbl.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(grp_lbl)

        self.group_list = QListWidget()
        self.group_list.setStyleSheet(f"border: 1px solid {BORDER}; border-radius: 6px;")
        self.group_list.setMaximumHeight(150)
        for g in self._groups:
            item = QListWidgetItem(g.name)
            item.setData(Qt.ItemDataRole.UserRole, g.id)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.group_list.addItem(item)
        layout.addWidget(self.group_list)

        row = QHBoxLayout()
        row.addStretch()
        cancel = _styled_secondary_btn("Cancelar", 110)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel)
        save = _styled_primary_btn("Guardar", 110)
        save.clicked.connect(self._validate)
        row.addWidget(save)
        layout.addLayout(row)

    def _load(self, u: User):
        self.full_name.setText(u.full_name)
        self.username.setText(u.username)
        self.active_check.setChecked(u.is_active)

    def set_assigned_groups(self, group_ids: list[int]):
        for i in range(self.group_list.count()):
            item = self.group_list.item(i)
            gid = item.data(Qt.ItemDataRole.UserRole)
            item.setCheckState(
                Qt.CheckState.Checked if gid in group_ids else Qt.CheckState.Unchecked
            )

    def _validate(self):
        ok = True
        if not self.full_name.text().strip():
            self.full_name.setStyleSheet(f"border: 2px solid {ERROR};")
            ok = False
        if not self.username.text().strip():
            self.username.setStyleSheet(f"border: 2px solid {ERROR};")
            ok = False
        if not self._user and not self.password.text():
            self.password.setStyleSheet(f"border: 2px solid {ERROR};")
            ok = False
        if ok:
            self.accept()

    def get_data(self) -> dict:
        group_ids = []
        for i in range(self.group_list.count()):
            item = self.group_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                group_ids.append(item.data(Qt.ItemDataRole.UserRole))
        return {
            "full_name": self.full_name.text().strip(),
            "username": self.username.text().strip(),
            "password": self.password.text() or None,
            "is_active": self.active_check.isChecked(),
            "group_ids": group_ids,
        }


class UserManagementView(QWidget):
    new_user_requested = pyqtSignal()
    edit_user_requested = pyqtSignal(int)
    toggle_user_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._users = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(16)

        title = QLabel("Gestion de Maestras")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_DARK};")
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        new_btn = _styled_primary_btn("+ Nueva Maestra", 180)
        new_btn.clicked.connect(self.new_user_requested.emit)
        btn_row.addWidget(new_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nombre", "Usuario", "Grupos", "Estado", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {BORDER};
                border-radius: 8px;
                alternate-background-color: {BG_INPUT};
            }}
            QHeaderView::section {{
                background-color: {PRIMARY};
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
        """)
        layout.addWidget(self.table)

    def load_users(self, users: list[dict]):
        self._users = users
        self.table.setRowCount(len(users))
        for r, u in enumerate(users):
            self.table.setItem(r, 0, QTableWidgetItem(u["full_name"]))
            self.table.setItem(r, 1, QTableWidgetItem(u["username"]))
            self.table.setItem(r, 2, QTableWidgetItem(u.get("groups", "—")))
            status = "Activa" if u["is_active"] else "Inactiva"
            self.table.setItem(r, 3, QTableWidgetItem(status))

            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(32, 28)
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{ background-color: {PRIMARY_DARK}; }}
            """)
            edit_btn.clicked.connect(lambda _, uid=u["id"]: self.edit_user_requested.emit(uid))
            al.addWidget(edit_btn)

            toggle_btn = QPushButton("🚫" if u["is_active"] else "✅")
            toggle_btn.setFixedSize(32, 28)
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {WARNING if u['is_active'] else SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 4px;
                }}
            """)
            toggle_btn.clicked.connect(lambda _, uid=u["id"]: self.toggle_user_requested.emit(uid))
            al.addWidget(toggle_btn)

            self.table.setCellWidget(r, 4, actions)
            self.table.setRowHeight(r, 40)
