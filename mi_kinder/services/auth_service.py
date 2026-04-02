"""Servicio de autenticacion."""
import bcrypt
import sqlite3
from mi_kinder.models.user import User
from mi_kinder.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.user_repo = UserRepository(conn)

    def login(self, username: str, password: str) -> User | None:
        """Intenta autenticar al usuario. Retorna User o None."""
        user = self.user_repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return user
        return None

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
