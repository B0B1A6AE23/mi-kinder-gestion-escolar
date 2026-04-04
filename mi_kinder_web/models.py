"""Modelos auxiliares para Flask-Login."""
from flask_login import UserMixin


class WebUser(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.full_name = row["full_name"]
        self.role = row["role"]
        self.photo_path = (
            row.get("photo_path")
            if hasattr(row, "get")
            else (row["photo_path"] if "photo_path" in row.keys() else None)
        )

    @property
    def is_directora(self):
        return self.role == "directora"
