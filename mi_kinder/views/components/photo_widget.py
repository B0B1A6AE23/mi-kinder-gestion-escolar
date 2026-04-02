"""Widget para mostrar y seleccionar foto de alumno."""
import os
import shutil
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from mi_kinder.theme.colors import *
from mi_kinder.config import get_photos_dir


class PhotoWidget(QWidget):
    photo_changed = pyqtSignal(str)  # nueva ruta relativa

    def __init__(self, size: int = 120, editable: bool = True):
        super().__init__()
        self._size = size
        self._editable = editable
        self._photo_path = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img_label = QLabel()
        self.img_label.setFixedSize(self._size, self._size)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_INPUT};
                border-radius: {self._size // 2}px;
                border: 3px solid {PRIMARY_LIGHT};
            }}
        """)
        self._show_placeholder()
        layout.addWidget(self.img_label)

        if self._editable:
            btn = QPushButton("📷 Cambiar foto")
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {PRIMARY};
                    border: 1px solid {PRIMARY};
                    border-radius: 6px;
                    font-size: 12px;
                    padding: 0 10px;
                }}
                QPushButton:hover {{ background-color: {HOVER_LIGHT}; }}
            """)
            btn.clicked.connect(self._select_photo)
            layout.addWidget(btn)

    def _show_placeholder(self):
        self.img_label.setText("🧒")
        self.img_label.setStyleSheet(f"""
            QLabel {{
                background-color: {BG_INPUT};
                border-radius: {self._size // 2}px;
                border: 3px solid {PRIMARY_LIGHT};
                font-size: {self._size // 3}px;
            }}
        """)

    def set_photo(self, photo_path: str):
        self._photo_path = photo_path
        if not photo_path:
            self._show_placeholder()
            return
        full_path = os.path.join(get_photos_dir(), photo_path) if not os.path.isabs(photo_path) else photo_path
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path).scaled(
                self._size, self._size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            # Recorte circular
            rounded = QPixmap(self._size, self._size)
            rounded.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, self._size, self._size)
            painter.setClipPath(path)
            offset_x = max(0, (pixmap.width() - self._size) // 2)
            offset_y = max(0, (pixmap.height() - self._size) // 2)
            painter.drawPixmap(0, 0, pixmap, offset_x, offset_y, self._size, self._size)
            painter.end()
            self.img_label.setPixmap(rounded)
            self.img_label.setStyleSheet(f"""
                QLabel {{
                    border-radius: {self._size // 2}px;
                    border: 3px solid {PRIMARY};
                }}
            """)
        else:
            self._show_placeholder()

    def _select_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar foto", "",
            "Imagenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if not path:
            return
        try:
            from PIL import Image
            img = Image.open(path)
            img = img.convert("RGB")
            img.thumbnail((400, 400), Image.LANCZOS)
            filename = os.path.basename(path)
            dest = os.path.join(get_photos_dir(), filename)
            # Nombre unico si ya existe
            base, ext = os.path.splitext(filename)
            import time
            dest = os.path.join(get_photos_dir(), f"{base}_{int(time.time())}.jpg")
            img.save(dest, "JPEG", quality=85)
            self._photo_path = os.path.basename(dest)
        except ImportError:
            # Sin Pillow, copiar directamente
            filename = os.path.basename(path)
            dest = os.path.join(get_photos_dir(), filename)
            shutil.copy2(path, dest)
            self._photo_path = filename

        self.set_photo(self._photo_path)
        self.photo_changed.emit(self._photo_path)

    def get_photo_path(self) -> str:
        return self._photo_path
