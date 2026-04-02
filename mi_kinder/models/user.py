"""Modelo de usuario."""
from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    DIRECTORA = "directora"
    MAESTRA = "maestra"


@dataclass
class User:
    id: int | None = None
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: UserRole = UserRole.MAESTRA
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""

    @staticmethod
    def from_row(row) -> "User":
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            role=UserRole(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
