import os
from flask import jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from app.utils import format_number, split_date

def resource_path(relative_path):
    """Retorna la ruta absoluta compatible con Render y PyInstaller."""
    try:
        base_path = sys._MEIPASS  # Para PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_pdf(request):
    try:
        required_fields = [
            "aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono",
            "correo", "fecha_evento", "fecha_ingreso", "placa", "marca", "modelo",
            "anio", "color", "asesor", "cedula_asesor",
            "cedula_responsable", "nombre_responsable", "correo_responsable", "telefono_responsable",
            "condicion", "provincia", "canton", "distrito", "cedula_empresa", "nombre_empresa",
            "cedula_estimacion", "nombre_estimacion"
        ]

        form_data = {field: request.form.get(field, "").strip() for field in required_fields}
        for field, value in form_data.items():
            if not value:
                return jsonify({"error": f"El campo {field} está vacío."}), 400

        # Formatear datos
        cedula_cliente = format_number(form_data["cedula"], is_cedula=True)
        telefono_cliente = format_number(form_data["telefono"])
        cedula_asesor = format_number(form_data["cedula_asesor"], is_cedula=True)
        cedula_responsable = format_number(form_data["cedula_responsable"], is_cedula=True)
        telefono_responsable = format_number(form_data["telefono_responsable"])
        cedula_empresa = format_number(form_data["cedula_empresa"], is_cedula=True)
        cedula_estimacion = format_number(form_data["cedula_estimacion"], is_cedula=True)

        # Fechas
        dia_evento, mes_evento, anio_evento = split_date(form_data["fecha_evento"])
        dia_ingreso, mes_ingreso, anio_ingreso = split_date(form_data["fecha_ingreso"])

        # Crear carpeta de guardado
        save_path = os.getenv("UPLOAD_FOLDER", "/opt/render/project/files/WABEDOCS")
        os.makedirs(save_path, exist_ok=True)

        case_number_folder = os.path.join(save_path, f"25-{form_data['consecutivo']}")
        os.makedirs(case_number_folder, exist_ok=True)

        # Definir rutas de salida
        temp_pdf1_path = os.path.join(case_number_folder, "temp_valoracion.pdf")
        temp_pdf2_path = os.path.join(case_number_folder, "temp_estimacion.pdf")
        output_pdf1_path = os.path.join(case_number_folder, f"{form_data['nombre']}_valoracion.pdf")
        output_pdf2_path = os.path.join(case_number_folder, f"{form_data['nombre']}_estimacion.pdf")

        # ✅ GENERAR PRIMER PDF (VALORACIÓN)
        c1 = canvas.Canvas(temp_pdf1_path, pagesize=letter)
        c1.setFont("Helvetica-Bold", 12)

        # Ajustar las posiciones de los textos para asegurarnos de que se impriman bien
        c1.drawString(100, 750, f"Número de Caso: {form_data['aviso']}")
        c1.drawString(100, 730, f"Placa: {form_data['placa']}")
        c1.drawString(100, 710, f"Nombre del Cliente: {form_data['nombre']}")
        c1.drawString(100, 690, f"Cédula: {cedula_cliente}")
        c1.drawString(100, 670, f"Teléfono: {telefono_cliente}")
        c1.drawString(100, 650, f"Correo: {form_data['correo']}")
        c1.drawString(100, 630, f"Fecha del Evento: {form_data['fecha_evento']}")
        c1.drawString(100, 610, f"Fecha de Ingreso: {form_data['fecha_ingreso']}")
        c1.drawString(100, 590, f"Asesor: {form_data['asesor']}")
        c1.drawString(100, 570, f"Provincia: {form_data['provincia']}")
        c1.drawString(100, 550, f"Condición: {form_data['condicion']}")

        c1.save()

        # ✅ GENERAR SEGUNDO PDF (ESTIMACIÓN)
        c2 = canvas.Canvas(temp_pdf2_path, pagesize=letter)
        c2.setFont("Helvetica-Bold", 12)

        c2.drawString(100, 750, f"Estimación para: {form_data['nombre_estimacion']}")
        c2.drawString(100, 730, f"Cédula: {cedula_estimacion}")
        c2.drawString(100, 710, f"Teléfono: {telefono_cliente}")
        c2.drawString(100, 690, f"Correo: {form_data['correo']}")

        c2.save()

        # ✅ FUNCION PARA COMBINAR PDFS CON LAS PLANTILLAS
        def combine_pdfs(template_path, temp_pdf_path, output_path):
            template_pdf = PdfReader(template_path)
            temp_pdf = PdfReader(temp_pdf_path)
            writer = PdfWriter()

            for page_number in range(len(template_pdf.pages)):
                template_page = template_pdf.pages[page_number]
                if page_number == 0:
                    template_page.merge_page(temp_pdf.pages[0])
                writer.add_page(template_page)

            with open(output_path, "wb") as output_file:
                writer.write(output_file)

        # ✅ RUTAS DE LAS PLANTILLAS PDF
        VALORACION_PDF_PATH = resource_path("pdfs/VALORACION.pdf")
        ESTIMACION_PDF_PATH = resource_path("pdfs/ESTIMACION.pdf")

        # ✅ COMBINAR LOS PDFS CON LAS PLANTILLAS
        combine_pdfs(VALORACION_PDF_PATH, temp_pdf1_path, output_pdf1_path)
        combine_pdfs(ESTIMACION_PDF_PATH, temp_pdf2_path, output_pdf2_path)

        # ✅ ELIMINAR ARCHIVOS TEMPORALES
        os.remove(temp_pdf1_path)
        os.remove(temp_pdf2_path)

        # ✅ RESPONDER CON LOS ARCHIVOS GENERADOS
        return send_file(output_pdf1_path, mimetype="application/pdf", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
