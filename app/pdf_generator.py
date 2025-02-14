import os
from flask import jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from app.utils import format_number, split_date



def generate_pdf(request):
    try:
        required_fields = ["aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono"]
        form_data = {field: request.form.get(field) for field in required_fields}

        # Validación
        for field, value in form_data.items():
            if not value:
                return jsonify({"error": f"El campo {field} está vacío"}), 400

        # Rutas
        save_path = os.getenv("UPLOAD_FOLDER", "/opt/render/project/files/WABEDOCS")
        os.makedirs(save_path, exist_ok=True)
        pdf_path = os.path.join(save_path, "documento.pdf")

        # Crear PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Nombre: {form_data['nombre']}")
        c.save()

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
