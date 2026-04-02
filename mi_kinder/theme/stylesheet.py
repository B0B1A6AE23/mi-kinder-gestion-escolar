"""QSS Stylesheet para la aplicacion Mi Kinder."""
from mi_kinder.theme.colors import *


def get_stylesheet() -> str:
    return f"""
    /* ===== GLOBAL ===== */
    QMainWindow, QDialog {{
        background-color: {BG_MAIN};
        color: {TEXT_PRIMARY};
        font-family: "Segoe UI", "Arial", sans-serif;
        font-size: 14px;
    }}

    QWidget {{
        font-family: "Segoe UI", "Arial", sans-serif;
    }}

    /* ===== LABELS ===== */
    QLabel {{
        color: {TEXT_PRIMARY};
    }}

    QLabel[class="title"] {{
        font-size: 24px;
        font-weight: bold;
        color: {PRIMARY_DARK};
    }}

    QLabel[class="subtitle"] {{
        font-size: 16px;
        color: {TEXT_SECONDARY};
    }}

    /* ===== BOTONES ===== */
    QPushButton {{
        background-color: {PRIMARY};
        color: {TEXT_LIGHT};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: bold;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background-color: {PRIMARY_DARK};
    }}

    QPushButton:pressed {{
        background-color: #BF360C;
    }}

    QPushButton:disabled {{
        background-color: {BORDER};
        color: {TEXT_MUTED};
    }}

    QPushButton[class="secondary"] {{
        background-color: {BG_CARD};
        color: {PRIMARY};
        border: 2px solid {PRIMARY};
    }}

    QPushButton[class="secondary"]:hover {{
        background-color: {HOVER_LIGHT};
    }}

    QPushButton[class="danger"] {{
        background-color: {ERROR};
    }}

    QPushButton[class="danger"]:hover {{
        background-color: #C62828;
    }}

    QPushButton[class="success"] {{
        background-color: {SUCCESS};
    }}

    /* ===== INPUTS ===== */
    QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {BG_INPUT};
        border: 2px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        color: {TEXT_PRIMARY};
        min-height: 20px;
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {BORDER_FOCUS};
        background-color: {BG_CARD};
    }}

    QDateEdit {{
        background-color: {BG_INPUT};
        border: 2px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        color: {TEXT_PRIMARY};
        min-height: 20px;
    }}

    QDateEdit:focus {{
        border-color: {BORDER_FOCUS};
        background-color: {BG_CARD};
    }}

    /* ===== COMBOBOX ===== */
    QComboBox {{
        background-color: {BG_INPUT};
        border: 2px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        color: {TEXT_PRIMARY};
        min-height: 20px;
    }}

    QComboBox:focus {{
        border-color: {BORDER_FOCUS};
    }}

    QComboBox::drop-down {{
        border: none;
        padding-right: 10px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 4px;
        selection-background-color: {PRIMARY_LIGHT};
        selection-color: {TEXT_PRIMARY};
    }}

    /* ===== TABLAS ===== */
    QTableWidget, QTableView {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
        gridline-color: {BORDER};
        selection-background-color: {PRIMARY_LIGHT};
        selection-color: {TEXT_PRIMARY};
        font-size: 13px;
    }}

    QTableWidget::item {{
        padding: 6px;
    }}

    QHeaderView::section {{
        background-color: {PRIMARY};
        color: {TEXT_LIGHT};
        padding: 8px;
        border: none;
        font-weight: bold;
        font-size: 13px;
    }}

    /* ===== TABS ===== */
    QTabWidget::pane {{
        border: 1px solid {BORDER};
        border-radius: 8px;
        background-color: {BG_CARD};
    }}

    QTabBar::tab {{
        background-color: {BG_INPUT};
        color: {TEXT_SECONDARY};
        padding: 10px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
        font-size: 13px;
    }}

    QTabBar::tab:selected {{
        background-color: {PRIMARY};
        color: {TEXT_LIGHT};
        font-weight: bold;
    }}

    QTabBar::tab:hover:!selected {{
        background-color: {PRIMARY_LIGHT};
        color: {TEXT_PRIMARY};
    }}

    /* ===== SCROLLBAR ===== */
    QScrollBar:vertical {{
        background-color: {BG_MAIN};
        width: 10px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {BORDER};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {PRIMARY_LIGHT};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ===== GROUPBOX ===== */
    QGroupBox {{
        border: 2px solid {BORDER};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
        color: {PRIMARY_DARK};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 5px;
    }}

    /* ===== MESSAGEBOX ===== */
    QMessageBox {{
        background-color: {BG_MAIN};
    }}

    /* ===== TOOLTIP ===== */
    QToolTip {{
        background-color: {TEXT_PRIMARY};
        color: {TEXT_LIGHT};
        border: none;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* ===== PROGRESS BAR ===== */
    QProgressBar {{
        border: 2px solid {BORDER};
        border-radius: 8px;
        text-align: center;
        background-color: {BG_INPUT};
        color: {TEXT_PRIMARY};
        min-height: 20px;
    }}

    QProgressBar::chunk {{
        background-color: {PRIMARY};
        border-radius: 6px;
    }}
    """
