from flask import Blueprint, render_template, request, jsonify, send_from_directory
import os
from app.utils import format_number, split_date
from app.pdf_generator import generate_pdf  # ✅ Importamos solo la función necesaria

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/ping")
def ping():
    return jsonify({"message": "Servidor Flask activo"})

@main.route("/generate_pdf", methods=["POST"])
def generate_pdf_route():
    return generate_pdf(request)  # ✅ Ahora la función está correctamente referenciada

@main.route("/download/<filename>")
def download_file(filename):
    if os.name == "nt":  # Windows
        save_path = os.path.join(os.environ["USERPROFILE"], "Downloads", "WABEDOCS")
    else:  # Render
        save_path = "/tmp/WABEDOCS"

    return send_from_directory(save_path, filename, as_attachment=True)
