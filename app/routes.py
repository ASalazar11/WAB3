from flask import Blueprint, render_template, request, jsonify, send_file
from app.utils import format_number, split_date
from app.pdf_generator import generate_pdf

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/ping")
def ping():
    return jsonify({"message": "Servidor Flask activo"})

@main.route("/generate_pdf", methods=["POST"])
def generate_pdf_route():
    return generate_pdf(request)
