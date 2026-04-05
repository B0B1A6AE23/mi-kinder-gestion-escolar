"""Motor PDF con fpdf2 para reportes escolares."""
import os
from fpdf import FPDF
from mi_kinder.models.student import Student
from mi_kinder.models.evaluation import EvaluationArea
from mi_kinder.models.school_year import Period


class SchoolPDF(FPDF):
    def __init__(self, school_info: dict, orientation="P"):
        super().__init__(orientation=orientation, unit="mm", format="Letter")
        self._school_info = school_info
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        school_name = self._school_info.get("name", "Mi Kinder")
        self.cell(0, 8, school_name, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        addr = self._school_info.get("address", "")
        phone = self._school_info.get("phone", "")
        if addr or phone:
            self.cell(0, 5, f"{addr}  |  Tel: {phone}", align="C", new_x="LMARGIN", new_y="NEXT")
        director = self._school_info.get("director_name", "")
        if director:
            self.cell(0, 5, f"Directora: {director}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y() + 2, self.w - 10, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, text: str):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(255, 112, 67)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {text}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def key_value(self, key: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.cell(45, 6, f"{key}:", new_x="END")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")


class PDFService:
    def generate_individual_report(self, data: dict, output_path: str):
        student: Student = data["student"]
        periods: list[Period] = data["periods"]
        areas: list[EvaluationArea] = data["areas"]
        eval_table: dict = data["eval_table"]
        observations = data.get("observations", [])
        school_info = data.get("school_info", {})

        pdf = SchoolPDF(school_info)
        pdf.alias_nb_pages()
        pdf.add_page()

        # Datos del alumno
        pdf.section_title("Datos del Alumno")
        pdf.key_value("Nombre", student.full_name)
        pdf.key_value("Grupo", student.group_name or "-")
        pdf.key_value("CURP", student.curp or "-")
        pdf.key_value("Fecha nacimiento", student.birth_date or "-")
        gender = {"M": "Nino", "F": "Nina"}.get(student.gender or "", "-")
        pdf.key_value("Genero", gender)
        pdf.key_value("Tutor", student.guardian_name or "-")
        pdf.key_value("Telefono tutor", student.guardian_phone or "-")
        pdf.ln(4)

        # Tabla de evaluaciones
        if areas and periods:
            pdf.section_title("Evaluaciones")

            col_w_name = 50
            n_periods = len(periods)
            avail = pdf.w - 20 - col_w_name
            col_w_per = min(avail / max(n_periods, 1), 35)

            # Header
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(62, 39, 35)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(col_w_name, 7, "Area", border=1, fill=True)
            for p in periods:
                pdf.cell(col_w_per, 7, p.name[:12], border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_text_color(0, 0, 0)

            # Rows
            for a in areas:
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(col_w_name, 7, a.name[:28], border=1)
                for p in periods:
                    ev = eval_table.get((a.id, p.id))
                    label = ev.grade_label if ev and ev.grade_label else "-"
                    if ev and ev.grade_color:
                        r, g, b = self._hex_to_rgb(ev.grade_color)
                        pdf.set_fill_color(r, g, b)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(col_w_per, 7, label, border=1, fill=True, align="C")
                        pdf.set_text_color(0, 0, 0)
                    else:
                        pdf.cell(col_w_per, 7, label, border=1, align="C")
                pdf.ln()

            pdf.ln(4)

        # Observaciones
        if observations:
            pdf.section_title("Observaciones")
            pdf.set_font("Helvetica", "", 9)
            for o in observations:
                date_str = o.created_at[:10] if o.created_at else ""
                pdf.multi_cell(0, 5, f"[{date_str}] {o.content}")
                pdf.ln(2)

        # Firmas
        pdf.ln(15)
        y = pdf.get_y()
        pdf.line(25, y, 85, y)
        pdf.line(pdf.w - 85, y, pdf.w - 25, y)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(pdf.w / 2 - 10, 5, "Firma de la Maestra", align="C")
        pdf.cell(pdf.w / 2 - 10, 5, "Firma de la Directora", align="C")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        pdf.output(output_path)

    def generate_group_report(self, data: dict, output_path: str):
        group = data["group"]
        students = data["students"]
        areas = data["areas"]
        periods = data["periods"]
        student_averages = data["student_averages"]
        school_info = data.get("school_info", {})

        pdf = SchoolPDF(school_info, orientation="L")
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.section_title(f"Reporte Grupal - {group.name}")
        pdf.key_value("Total alumnos", str(len(students)))
        pdf.ln(4)

        # Ranking de alumnos
        pdf.section_title("Ranking de Alumnos")
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(62, 39, 35)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(10, 7, "#", border=1, fill=True, align="C")
        pdf.cell(70, 7, "Alumno", border=1, fill=True)
        pdf.cell(30, 7, "Promedio", border=1, fill=True, align="C")
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        for i, sa in enumerate(student_averages):
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(10, 6, str(i + 1), border=1, align="C")
            pdf.cell(70, 6, sa["student"].full_name, border=1)
            pdf.cell(30, 6, f"{sa['average']:.1f}", border=1, align="C")
            pdf.ln()

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        pdf.output(output_path)

    def generate_general_report(self, data: dict, output_path: str):
        groups = data["groups"]
        areas = data["areas"]
        group_data = data["group_data"]
        school_info = data.get("school_info", {})

        pdf = SchoolPDF(school_info, orientation="L")
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.section_title("Reporte General de la Escuela")
        pdf.ln(2)

        # Tabla comparativa: grupos vs areas
        col_w_name = 45
        n_areas = len(areas)
        avail = pdf.w - 20 - col_w_name
        col_w_area = min(avail / max(n_areas, 1), 30)

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(62, 39, 35)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(col_w_name, 7, "Grupo", border=1, fill=True)
        for a in areas:
            pdf.cell(col_w_area, 7, a.name[:15], border=1, fill=True, align="C")
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        for gd in group_data:
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(col_w_name, 6, gd["group"].name, border=1)
            for a in areas:
                val = gd["averages"].get(a.name)
                text = f"{val:.1f}" if val else "-"
                pdf.cell(col_w_area, 6, text, border=1, align="C")
            pdf.ln()

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        pdf.output(output_path)

    def generate_boleta(self, data: dict, output_path: str):
        self.generate_individual_report(data, output_path)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return (128, 128, 128)
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
