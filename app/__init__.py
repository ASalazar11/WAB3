import os
import sys  # ✅ Se agregó esta línea
from flask import Flask
from config import Config

def resource_path(relative_path):
    """Retorna la ruta absoluta, compatible con PyInstaller y entornos de despliegue."""
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_app():
    app = Flask(__name__, 
                template_folder=resource_path("templates"), 
                static_folder=resource_path("static"))

    app.config.from_object(Config)

    from app.routes import main  # ✅ Se mueve aquí después de crear la app
    app.register_blueprint(main)

    return app
