"""Repositorio de grupos escolares."""
import sqlite3
from mi_kinder.models.group import Group
from mi_kinder.repositories.base_repository import BaseRepository


class GroupRepository(BaseRepository):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "groups_")

    def get_all(self, school_year_id: int, active_only: bool = True) -> list[Group]:
        sql = """
            SELECT g.*,
                   u.full_name as teacher_name,
                   COUNT(DISTINCT s.id) as student_count
            FROM groups_ g
            LEFT JOIN user_group_assignments uga ON uga.group_id = g.id
            LEFT JOIN users u ON u.id = uga.user_id
            LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
            WHERE g.school_year_id = ?
        """
        params: list = [school_year_id]
        if active_only:
            sql += " AND g.is_active = 1"
        sql += " GROUP BY g.id ORDER BY g.name"
        return [Group.from_row(r) for r in self._fetch_all(sql, tuple(params))]

    def get_by_id(self, group_id: int) -> Group | None:
        row = self._fetch_one(
            """SELECT g.*,
                      u.full_name as teacher_name,
                      COUNT(DISTINCT s.id) as student_count
               FROM groups_ g
               LEFT JOIN user_group_assignments uga ON uga.group_id = g.id
               LEFT JOIN users u ON u.id = uga.user_id
               LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
               WHERE g.id = ?
               GROUP BY g.id""",
            (group_id,),
        )
        return Group.from_row(row) if row else None

    def get_for_user(self, school_year_id: int, user_id: int) -> list[Group]:
        sql = """
            SELECT g.*,
                   u.full_name as teacher_name,
                   COUNT(DISTINCT s.id) as student_count
            FROM groups_ g
            INNER JOIN user_group_assignments uga ON uga.group_id = g.id AND uga.user_id = ?
            LEFT JOIN users u ON u.id = uga.user_id
            LEFT JOIN students s ON s.group_id = g.id AND s.is_active = 1
            WHERE g.school_year_id = ? AND g.is_active = 1
            GROUP BY g.id ORDER BY g.name
        """
        return [Group.from_row(r) for r in self._fetch_all(sql, (user_id, school_year_id))]

    def create(self, group: Group) -> int:
        cursor = self._execute(
            """INSERT INTO groups_ (school_year_id, name, grade_level, capacity, is_active)
               VALUES (?, ?, ?, ?, ?)""",
            (group.school_year_id, group.name, group.grade_level or None,
             group.capacity, int(group.is_active)),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update(self, group: Group):
        self._execute(
            """UPDATE groups_ SET name=?, grade_level=?, capacity=?, is_active=?,
               updated_at=datetime('now') WHERE id=?""",
            (group.name, group.grade_level or None, group.capacity,
             int(group.is_active), group.id),
        )
        self.conn.commit()
