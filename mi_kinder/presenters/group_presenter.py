"""Presenter para la gestion de grupos."""
import sqlite3
from mi_kinder.services.session import Session
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.user_repository import UserRepository
from mi_kinder.models.group import Group
from mi_kinder.views.groups.group_list_view import GroupListView
from mi_kinder.views.groups.group_form_dialog import GroupFormDialog
from mi_kinder.views.components.confirmation_dialog import confirm, info, alert


class GroupPresenter:
    def __init__(self, view: GroupListView, conn: sqlite3.Connection):
        self._view = view
        self._group_repo = GroupRepository(conn)
        self._user_repo = UserRepository(conn)
        self._session = Session.get()

        view.new_group_requested.connect(self._on_new)
        view.edit_group_requested.connect(self._on_edit)
        view.delete_group_requested.connect(self._on_delete)

    def load(self):
        if not self._session.current_year:
            self._view.load_groups([])
            return
        groups = self._group_repo.get_all(self._session.current_year.id)
        self._view.load_groups(groups)

    def _on_new(self):
        teachers = self._user_repo.get_maestras()
        dlg = GroupFormDialog(self._view, teachers=teachers)
        if dlg.exec():
            data = dlg.get_data()
            group = Group(
                school_year_id=self._session.current_year.id,
                name=data["name"],
                grade_level=data["grade_level"],
                capacity=data["capacity"],
            )
            group_id = self._group_repo.create(group)
            if data["teacher_id"]:
                self._user_repo.assign_to_group(data["teacher_id"], group_id)
            self.load()

    def _on_edit(self, group_id: int):
        group = self._group_repo.get_by_id(group_id)
        if not group:
            return
        teachers = self._user_repo.get_maestras()
        dlg = GroupFormDialog(self._view, group=group, teachers=teachers)
        if dlg.exec():
            data = dlg.get_data()
            group.name = data["name"]
            group.grade_level = data["grade_level"]
            group.capacity = data["capacity"]
            self._group_repo.update(group)

            # Actualizar asignacion de maestra
            rows = self._user_repo._fetch_all(
                "SELECT user_id FROM user_group_assignments WHERE group_id = ?", (group_id,)
            )
            for r in rows:
                self._user_repo.remove_from_group(r["user_id"], group_id)
            if data["teacher_id"]:
                self._user_repo.assign_to_group(data["teacher_id"], group_id)
            self.load()

    def _on_delete(self, group_id: int):
        group = self._group_repo.get_by_id(group_id)
        if not group:
            return
        if group.student_count > 0:
            alert(self._view, "No se puede eliminar",
                  f"El grupo '{group.name}' tiene {group.student_count} alumnos activos.\n"
                  "Transfiere o da de baja a los alumnos antes de eliminar el grupo.")
            return
        if confirm(self._view, "Eliminar grupo",
                   f"¿Eliminar el grupo '{group.name}'?\nEsta accion no se puede deshacer."):
            self._group_repo.delete(group_id)
            self.load()
