"""Repositorio base con operaciones CRUD genericas."""
import json
import sqlite3
from datetime import datetime


class BaseRepository:
    def __init__(self, conn: sqlite3.Connection, table_name: str):
        self.conn = conn
        self.table_name = table_name

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def _fetch_one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        return self.conn.execute(sql, params).fetchone()

    def _fetch_all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, params).fetchall()

    def get_by_id(self, record_id: int) -> sqlite3.Row | None:
        return self._fetch_one(
            f"SELECT * FROM {self.table_name} WHERE id = ?", (record_id,)
        )

    def delete(self, record_id: int, user_id: int | None = None):
        old = self.get_by_id(record_id)
        self._execute(
            f"DELETE FROM {self.table_name} WHERE id = ?", (record_id,)
        )
        if old:
            self._audit("DELETE", record_id, dict(old), None, user_id)
        self.conn.commit()

    def _audit(
        self,
        action: str,
        record_id: int | None,
        old_values: dict | None,
        new_values: dict | None,
        user_id: int | None = None,
    ):
        self._execute(
            """INSERT INTO audit_log (user_id, action, table_name, record_id, old_values, new_values)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                action,
                self.table_name,
                record_id,
                json.dumps(old_values, ensure_ascii=False) if old_values else None,
                json.dumps(new_values, ensure_ascii=False) if new_values else None,
            ),
        )
