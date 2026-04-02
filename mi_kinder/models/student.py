"""Modelo de alumno."""
from dataclasses import dataclass


@dataclass
class Student:
    id: int | None = None
    group_id: int = 0
    first_name: str = ""
    last_name: str = ""
    second_last_name: str = ""
    curp: str = ""
    birth_date: str = ""
    gender: str | None = None
    photo_path: str = ""
    enrollment_date: str = ""
    guardian_name: str = ""
    guardian_phone: str = ""
    guardian_email: str = ""
    address: str = ""
    blood_type: str = ""
    allergies: str = ""
    medical_notes: str = ""
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    # Campos calculados
    group_name: str = ""

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        if self.second_last_name:
            parts.append(self.second_last_name)
        return " ".join(parts)

    @staticmethod
    def from_row(row) -> "Student":
        s = Student(
            id=row["id"],
            group_id=row["group_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            second_last_name=row["second_last_name"] or "",
            curp=row["curp"] or "",
            birth_date=row["birth_date"] or "",
            gender=row["gender"],
            photo_path=row["photo_path"] or "",
            enrollment_date=row["enrollment_date"],
            guardian_name=row["guardian_name"] or "",
            guardian_phone=row["guardian_phone"] or "",
            guardian_email=row["guardian_email"] or "",
            address=row["address"] or "",
            blood_type=row["blood_type"] or "",
            allergies=row["allergies"] or "",
            medical_notes=row["medical_notes"] or "",
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        keys = row.keys()
        if "group_name" in keys:
            s.group_name = row["group_name"] or ""
        return s


@dataclass
class StudentTransfer:
    id: int | None = None
    student_id: int = 0
    from_group_id: int = 0
    to_group_id: int = 0
    transfer_date: str = ""
    reason: str = ""
    transferred_by: int | None = None
    created_at: str = ""

    @staticmethod
    def from_row(row) -> "StudentTransfer":
        return StudentTransfer(
            id=row["id"],
            student_id=row["student_id"],
            from_group_id=row["from_group_id"],
            to_group_id=row["to_group_id"],
            transfer_date=row["transfer_date"],
            reason=row["reason"] or "",
            transferred_by=row["transferred_by"],
            created_at=row["created_at"],
        )
