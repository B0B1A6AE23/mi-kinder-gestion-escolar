"""Aplicacion principal Mi Kinder - Orquesta login, ventana principal y servicios."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from mi_kinder.database.connection import get_connection, close_connection
from mi_kinder.database.migrations import run_migrations
from mi_kinder.database.seed import seed_database
from mi_kinder.services.auth_service import AuthService
from mi_kinder.services.session import Session
from mi_kinder.repositories.user_repository import UserRepository
from mi_kinder.repositories.school_year_repository import SchoolYearRepository
from mi_kinder.repositories.group_repository import GroupRepository
from mi_kinder.repositories.student_repository import StudentRepository
from mi_kinder.views.login_view import LoginView
from mi_kinder.views.main_window import MainWindow
from mi_kinder.theme.stylesheet import get_stylesheet

# Vistas Fase 2
from mi_kinder.views.groups.group_list_view import GroupListView
from mi_kinder.views.students.student_list_view import StudentListView
from mi_kinder.views.students.student_detail_view import StudentDetailView
from mi_kinder.views.settings.settings_view import SettingsView

# Presenters Fase 2
from mi_kinder.presenters.group_presenter import GroupPresenter
from mi_kinder.presenters.student_presenter import StudentPresenter
from mi_kinder.presenters.settings_presenter import SettingsPresenter

# Fase 3: Evaluaciones
from mi_kinder.views.evaluations.evaluation_grid_view import EvaluationGridView
from mi_kinder.presenters.evaluation_presenter import (
    EvaluationPresenter, AreaPresenter, ScalePresenter,
)

# Fase 4: Reportes
from mi_kinder.views.reports.report_view import ReportView
from mi_kinder.presenters.report_presenter import ReportPresenter

# Fase 5: Graficas
from mi_kinder.views.charts.chart_view import ChartView
from mi_kinder.presenters.chart_presenter import ChartPresenter

# Fase 6: Asistencia y Usuarios
from mi_kinder.views.attendance.attendance_view import AttendanceView
from mi_kinder.presenters.attendance_presenter import AttendancePresenter
from mi_kinder.views.users.user_management_view import UserManagementView
from mi_kinder.presenters.user_presenter import UserPresenter
from mi_kinder.repositories.attendance_repository import AttendanceRepository


class MiKinderApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Mi Kinder")
        self.app.setStyleSheet(get_stylesheet())

        self.conn = get_connection()
        run_migrations(self.conn)
        seed_database(self.conn)

        self.auth_service = AuthService(self.conn)
        self.session = Session.get()

        self.login_view: LoginView | None = None
        self.main_window: MainWindow | None = None

    def run(self) -> int:
        self._show_login()
        return self.app.exec()

    def _show_login(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.session.logout()

        self.login_view = LoginView()
        self.login_view.login_requested.connect(self._on_login)
        self.login_view.setWindowTitle("Mi Kinder - Iniciar Sesion")
        self.login_view.setMinimumSize(500, 600)
        self.login_view.show()

    def _on_login(self, username: str, password: str):
        user = self.auth_service.login(username, password)
        if not user:
            self.login_view.show_error("Usuario o contrasena incorrectos")
            return

        year_repo = SchoolYearRepository(self.conn)
        user_repo = UserRepository(self.conn)
        active_year = year_repo.get_active()
        group_ids = user_repo.get_groups_for_user(user.id)
        self.session.login(user, active_year, group_ids)

        self.login_view.close()
        self._show_main()

    def _show_main(self):
        self.main_window = MainWindow(is_directora=self.session.is_directora)
        self.main_window.logout_requested.connect(self._show_login)

        # Dashboard
        self.main_window.dashboard.navigate_to.connect(
            self.main_window.sidebar.select_section
        )

        # ── Grupos ──
        group_view = GroupListView(can_edit=self.session.is_directora)
        group_presenter = GroupPresenter(group_view, self.conn)
        self.main_window.add_section("groups", group_view)
        # Cargar al mostrar
        self.main_window.sidebar.section_changed.connect(
            lambda s: group_presenter.load() if s == "groups" else None
        )

        # ── Alumnos ──
        student_list = StudentListView(can_edit=True)
        student_detail = StudentDetailView(can_edit=self.session.is_directora)
        student_presenter = StudentPresenter(student_list, student_detail, self.conn)

        # Contenedor con stack interno para list/detail
        from PyQt6.QtWidgets import QStackedWidget
        student_stack = QStackedWidget()
        student_stack.addWidget(student_list)
        student_stack.addWidget(student_detail)
        self.main_window.add_section("students", student_stack)

        # Navegar a detalle al ver alumno
        student_list.view_student_requested.connect(
            lambda sid: (student_presenter._on_view(sid), student_stack.setCurrentWidget(student_detail))
        )
        # Volver a lista desde detalle
        student_detail.back_requested.connect(
            lambda: student_stack.setCurrentWidget(student_list)
        )
        self.main_window.sidebar.section_changed.connect(
            lambda s: (student_presenter.load(), student_stack.setCurrentWidget(student_list))
            if s == "students" else None
        )

        # ── Evaluaciones ──
        eval_grid = EvaluationGridView(can_edit=True)
        eval_presenter = EvaluationPresenter(eval_grid, self.conn)
        self.main_window.add_section("evaluations", eval_grid)
        self.main_window.sidebar.section_changed.connect(
            lambda s: eval_presenter.load() if s == "evaluations" else None
        )

        # ── Reportes (Fase 4) ──
        report_view = ReportView(is_directora=self.session.is_directora)
        report_presenter = ReportPresenter(report_view, self.conn)
        self.main_window.add_section("reports", report_view)
        self.main_window.sidebar.section_changed.connect(
            lambda s: report_presenter.load() if s == "reports" else None
        )

        # ── Graficas (Fase 5) ──
        chart_view = ChartView(is_directora=self.session.is_directora)
        chart_presenter = ChartPresenter(chart_view, self.conn)
        self.main_window.add_section("charts", chart_view)
        self.main_window.sidebar.section_changed.connect(
            lambda s: chart_presenter.load() if s == "charts" else None
        )

        # ── Asistencia (Fase 6) ──
        att_view = AttendanceView()
        att_presenter = AttendancePresenter(att_view, self.conn)
        self.main_window.add_section("attendance", att_view)
        self.main_window.sidebar.section_changed.connect(
            lambda s: att_presenter.load() if s == "attendance" else None
        )

        # ── Ajustes (solo directora) ──
        if self.session.is_directora:
            settings_view = SettingsView()
            settings_presenter = SettingsPresenter(settings_view, self.conn)
            area_presenter = AreaPresenter(settings_view.area_widget, self.conn)
            scale_presenter = ScalePresenter(settings_view.scale_widget, self.conn)
            self.main_window.add_section("settings", settings_view)
            self.main_window.sidebar.section_changed.connect(
                lambda s: (settings_presenter.load(), area_presenter.load(), scale_presenter.load())
                if s == "settings" else None
            )

        # ── Usuarios (solo directora, Fase 6) ──
        if self.session.is_directora:
            user_view = UserManagementView()
            user_presenter = UserPresenter(user_view, self.conn)
            self.main_window.add_section("users", user_view)
            self.main_window.sidebar.section_changed.connect(
                lambda s: user_presenter.load() if s == "users" else None
            )

        # Dashboard stats
        self._update_dashboard()

        year_name = self.session.current_year.name if self.session.current_year else "Sin ciclo activo"
        self.main_window.set_status(
            f"Mi Kinder v1.0.0  |  {year_name}  |  {self.session.current_user.full_name}"
        )
        self.main_window.dashboard.set_welcome(self.session.current_user.full_name)
        self.main_window.show()

    def _update_dashboard(self):
        if not self.session.current_year:
            self.main_window.dashboard.update_stats(0, 0, 0, 0)
            return

        year_id = self.session.current_year.id
        student_repo = StudentRepository(self.conn)
        group_repo = GroupRepository(self.conn)
        user_repo = UserRepository(self.conn)
        att_repo = AttendanceRepository(self.conn)

        total_students = student_repo.count_all(year_id)
        total_groups = len(group_repo.get_all(year_id))
        total_teachers = len(user_repo.get_maestras())

        # Asistencia de hoy promedio de todos los grupos
        from datetime import date
        today = date.today().isoformat()
        groups = group_repo.get_all(year_id)
        if groups:
            rates = [att_repo.get_attendance_rate(g.id, today, today) for g in groups]
            avg_att = sum(rates) / len(rates) if rates else 0
        else:
            avg_att = 0

        self.main_window.dashboard.update_stats(total_students, total_groups, total_teachers, avg_att)

    def cleanup(self):
        close_connection()
        Session.reset()
