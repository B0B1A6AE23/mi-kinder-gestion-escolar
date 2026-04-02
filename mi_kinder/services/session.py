"""Sesion singleton: usuario actual, ciclo activo, permisos."""
from mi_kinder.models.user import User, UserRole
from mi_kinder.models.school_year import SchoolYear


class Session:
    _instance: "Session | None" = None

    def __init__(self):
        self.current_user: User | None = None
        self.current_year: SchoolYear | None = None
        self._user_group_ids: set[int] = set()

    @classmethod
    def get(cls) -> "Session":
        if cls._instance is None:
            cls._instance = Session()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def login(self, user: User, year: SchoolYear | None, group_ids: list[int]):
        self.current_user = user
        self.current_year = year
        self._user_group_ids = set(group_ids)

    def logout(self):
        self.current_user = None
        self.current_year = None
        self._user_group_ids.clear()

    @property
    def is_directora(self) -> bool:
        return self.current_user is not None and self.current_user.role == UserRole.DIRECTORA

    def can_access_group(self, group_id: int) -> bool:
        if self.is_directora:
            return True
        return group_id in self._user_group_ids

    def can_manage_users(self) -> bool:
        return self.is_directora

    def can_manage_settings(self) -> bool:
        return self.is_directora

    def can_view_general_reports(self) -> bool:
        return self.is_directora
