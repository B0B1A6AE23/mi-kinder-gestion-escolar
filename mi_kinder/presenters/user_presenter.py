"""Presenter para gestion de usuarios (maestras)."""
import sqlite3
import bcrypt
from mi_kinder.services.session import Session
from mi_kinder.repositories.user_repository import UserRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.models.user import User, UserRole
from mi_kinder.views.users.user_management_view import UserManagementView, UserFormDialog
from mi_kinder.views.components.confirmation_dialog import info


class UserPresenter:
    def __init__(self, view: UserManagementView, conn: sqlite3.Connection):
        self._view = view
        self._conn = conn
        self._user_repo = UserRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._session = Session.get()

        view.new_user_requested.connect(self._on_new)
        view.edit_user_requested.connect(self._on_edit)
        view.toggle_user_requested.connect(self._on_toggle)

    def load(self):
        maestras = self._user_repo.get_maestras(active_only=False)
        user_data = []
        for u in maestras:
            group_ids = self._user_repo.get_groups_for_user(u.id)
            groups = []
            for gid in group_ids:
                g = self._group_repo.get_by_id(gid)
                if g:
                    groups.append(g.name)
            user_data.append({
                "id": u.id,
                "full_name": u.full_name,
                "username": u.username,
                "is_active": u.is_active,
                "groups": ", ".join(groups) if groups else "Sin asignar",
            })
        self._view.load_users(user_data)

    def _on_new(self):
        year = self._session.current_year
        groups = self._group_repo.get_all(year.id) if year else []
        dlg = UserFormDialog(self._view, groups=groups)
        if dlg.exec():
            data = dlg.get_data()
            pw_hash = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
            self._conn.execute(
                """INSERT INTO users (username, password_hash, full_name, role, is_active)
                   VALUES (?, ?, ?, ?, ?)""",
                (data["username"], pw_hash, data["full_name"], UserRole.MAESTRA.value,
                 int(data["is_active"])),
            )
            self._conn.commit()
            user_id = self._conn.execute(
                "SELECT id FROM users WHERE username = ?", (data["username"],)
            ).fetchone()["id"]

            self._assign_groups(user_id, data["group_ids"])
            self.load()
            info(self._view, "Maestra creada", f"La maestra '{data['full_name']}' fue creada.")

    def _on_edit(self, user_id: int):
        user = self._user_repo.get_by_id(user_id)
        if not user:
            return
        year = self._session.current_year
        groups = self._group_repo.get_all(year.id) if year else []
        dlg = UserFormDialog(self._view, user=user, groups=groups)
        assigned = self._user_repo.get_groups_for_user(user_id)
        dlg.set_assigned_groups(assigned)

        if dlg.exec():
            data = dlg.get_data()
            self._conn.execute(
                """UPDATE users SET full_name=?, username=?, is_active=? WHERE id=?""",
                (data["full_name"], data["username"], int(data["is_active"]), user_id),
            )
            if data["password"]:
                pw_hash = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
                self._conn.execute(
                    "UPDATE users SET password_hash=? WHERE id=?", (pw_hash, user_id),
                )
            self._conn.commit()
            self._assign_groups(user_id, data["group_ids"])
            self.load()

    def _on_toggle(self, user_id: int):
        user = self._user_repo.get_by_id(user_id)
        if not user:
            return
        new_active = 0 if user.is_active else 1
        self._conn.execute(
            "UPDATE users SET is_active=? WHERE id=?", (new_active, user_id),
        )
        self._conn.commit()
        self.load()

    def _assign_groups(self, user_id: int, group_ids: list[int]):
        self._conn.execute(
            "DELETE FROM user_group_assignments WHERE user_id = ?", (user_id,)
        )
        for gid in group_ids:
            self._conn.execute(
                "INSERT INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
                (user_id, gid),
            )
        self._conn.commit()
