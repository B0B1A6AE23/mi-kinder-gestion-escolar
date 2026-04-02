"""Presenter para la gestion de alumnos."""
import sqlite3
from mi_kinder.services.session import Session
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.evaluation_repository import EvaluationRepository
from mi_kinder.repositories.observation_repository import ObservationRepository
from mi_kinder.models.student import Student
from mi_kinder.views.students.student_list_view import StudentListView
from mi_kinder.views.students.student_detail_view import StudentDetailView
from mi_kinder.views.students.student_form_dialog import StudentFormDialog
from mi_kinder.views.components.confirmation_dialog import confirm, alert
from datetime import date


class StudentPresenter:
    def __init__(self, list_view: StudentListView, detail_view: StudentDetailView, conn: sqlite3.Connection):
        self._list = list_view
        self._detail = detail_view
        self._student_repo = StudentRepository(conn)
        self._group_repo = GroupRepository(conn)
        self._eval_repo = EvaluationRepository(conn)
        self._obs_repo = ObservationRepository(conn)
        self._session = Session.get()
        self._groups = []

        list_view.new_student_requested.connect(self._on_new)
        list_view.edit_student_requested.connect(self._on_edit)
        list_view.view_student_requested.connect(self._on_view)
        list_view.delete_student_requested.connect(self._on_delete)
        list_view.group_changed.connect(self._on_group_filter)

        detail_view.back_requested.connect(lambda: None)  # Conectado externamente
        detail_view.edit_requested.connect(self._on_edit)

    def load(self):
        if not self._session.current_year:
            self._list.load_groups([])
            self._list.load_students([])
            return

        year_id = self._session.current_year.id
        if self._session.is_directora:
            self._groups = self._group_repo.get_all(year_id)
        else:
            self._groups = self._group_repo.get_for_user(year_id, self._session.current_user.id)

        self._list.load_groups(self._groups)
        self._load_students(-1)

    def _load_students(self, group_id: int):
        if group_id == -1:
            students = []
            for g in self._groups:
                students.extend(self._student_repo.get_by_group(g.id))
        else:
            students = self._student_repo.get_by_group(group_id)
        self._list.load_students(students)

    def _on_group_filter(self, group_id: int):
        self._load_students(group_id)

    def _on_new(self):
        dlg = StudentFormDialog(self._list, groups=self._groups)
        if dlg.exec():
            data = dlg.get_data()
            student = Student(
                group_id=data["group_id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                second_last_name=data["second_last_name"],
                curp=data["curp"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                photo_path=data["photo_path"],
                enrollment_date=date.today().isoformat(),
                guardian_name=data["guardian_name"],
                guardian_phone=data["guardian_phone"],
                guardian_email=data["guardian_email"],
                blood_type=data["blood_type"],
                allergies=data["allergies"],
                medical_notes=data["medical_notes"],
            )
            self._student_repo.create(student)
            self.load()

    def _on_edit(self, student_id: int):
        student = self._student_repo.get_by_id(student_id)
        if not student:
            return
        dlg = StudentFormDialog(self._list, student=student, groups=self._groups)
        if dlg.exec():
            data = dlg.get_data()
            student.first_name = data["first_name"]
            student.last_name = data["last_name"]
            student.second_last_name = data["second_last_name"]
            student.curp = data["curp"]
            student.birth_date = data["birth_date"]
            student.gender = data["gender"]
            student.group_id = data["group_id"]
            student.photo_path = data["photo_path"]
            student.guardian_name = data["guardian_name"]
            student.guardian_phone = data["guardian_phone"]
            student.guardian_email = data["guardian_email"]
            student.blood_type = data["blood_type"]
            student.allergies = data["allergies"]
            student.medical_notes = data["medical_notes"]
            self._student_repo.update(student)
            self.load()

    def _on_view(self, student_id: int):
        student = self._student_repo.get_by_id(student_id)
        if not student:
            return
        evaluations = self._eval_repo.get_for_student(student_id)
        observations = self._obs_repo.get_by_student(student_id)
        self._detail.load_student(student)
        self._detail.load_evaluations(evaluations)
        self._detail.load_observations(observations)
        # La vista que usa este presenter conecta back_requested para volver

    def _on_delete(self, student_id: int):
        student = self._student_repo.get_by_id(student_id)
        if not student:
            return
        if confirm(self._list, "Dar de baja",
                   f"¿Dar de baja al alumno '{student.full_name}'?\n"
                   "Sus evaluaciones y datos se conservan."):
            student.is_active = False
            self._student_repo.update(student)
            self.load()
