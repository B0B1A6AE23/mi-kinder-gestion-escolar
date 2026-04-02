"""Repositorio de usuarios."""
import sqlite3
from mi_kinder.models.user import User
from mi_kinder.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "users")

    def get_by_username(self, username: str) -> User | None:
        row = self._fetch_one(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        return User.from_row(row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        row = self._fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return User.from_row(row) if row else None

    def get_all(self, active_only: bool = True) -> list[User]:
        sql = "SELECT * FROM users"
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY full_name"
        return [User.from_row(r) for r in self._fetch_all(sql)]

    def get_maestras(self, active_only: bool = True) -> list[User]:
        sql = "SELECT * FROM users WHERE role = 'maestra'"
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY full_name"
        return [User.from_row(r) for r in self._fetch_all(sql)]

    def create(self, user: User) -> int:
        cursor = self._execute(
            """INSERT INTO users (username, password_hash, full_name, role, is_active)
               VALUES (?, ?, ?, ?, ?)""",
            (user.username, user.password_hash, user.full_name, user.role.value, int(user.is_active)),
        )
        user_id = cursor.lastrowid
        self._audit("INSERT", user_id, None, {"username": user.username, "role": user.role.value})
        self.conn.commit()
        return user_id

    def update(self, user: User, editor_id: int | None = None):
        old = self.get_by_id(user.id)
        self._execute(
            """UPDATE users SET username=?, password_hash=?, full_name=?, role=?,
               is_active=?, updated_at=datetime('now') WHERE id=?""",
            (user.username, user.password_hash, user.full_name, user.role.value,
             int(user.is_active), user.id),
        )
        self._audit("UPDATE", user.id, {"full_name": old.full_name} if old else None,
                     {"full_name": user.full_name}, editor_id)
        self.conn.commit()

    def get_groups_for_user(self, user_id: int) -> list[int]:
        rows = self._fetch_all(
            "SELECT group_id FROM user_group_assignments WHERE user_id = ?",
            (user_id,),
        )
        return [r["group_id"] for r in rows]

    def assign_to_group(self, user_id: int, group_id: int):
        self._execute(
            "INSERT OR IGNORE INTO user_group_assignments (user_id, group_id) VALUES (?, ?)",
            (user_id, group_id),
        )
        self.conn.commit()

    def remove_from_group(self, user_id: int, group_id: int):
        self._execute(
            "DELETE FROM user_group_assignments WHERE user_id = ? AND group_id = ?",
            (user_id, group_id),
        )
        self.conn.commit()
