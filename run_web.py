"""Inicia el servidor web Mi Kinder."""
from mi_kinder_web.app import create_app

app = create_app()

if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print()
    print("=" * 60)
    print("  Mi Kinder Web - Servidor Iniciado")
    print("=" * 60)
    print()
    print(f"  Desde esta PC:    http://localhost:5000")
    print(f"  Desde otra PC:    http://{local_ip}:5000")
    print()
    print("  Usuario: directora")
    print("  Contrasena: admin123")
    print()
    print("  Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
