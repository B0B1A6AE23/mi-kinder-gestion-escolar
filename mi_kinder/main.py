"""Punto de entrada de Mi Kinder."""
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mi_kinder.app import MiKinderApp


def main():
    app = MiKinderApp()
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
