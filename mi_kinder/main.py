"""Punto de entrada de Mi Kinder."""
import sys
import os
import traceback

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _exception_hook(exc_type, exc_value, exc_tb):
    """Captura excepciones no manejadas y las muestra en un dialogo."""
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        app = QApplication.instance()
        if app:
            QMessageBox.critical(
                None, "Error inesperado",
                f"Ocurrio un error inesperado:\n\n{msg[:500]}\n\n"
                "La aplicacion intentara continuar.",
            )
    except Exception:
        pass
    # Log to file
    try:
        from mi_kinder.config import get_data_dir
        log_path = os.path.join(get_data_dir(), "error.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n{msg}\n")
    except Exception:
        pass


def main():
    sys.excepthook = _exception_hook

    from mi_kinder.app import MiKinderApp
    app = MiKinderApp()
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
