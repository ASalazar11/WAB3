import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/opt/render/project/files/WABEDOCS")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
