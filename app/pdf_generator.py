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
    # Verifica si los campos están presentes
        required_fields = [
            "aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono",
            "correo", "fecha_evento", "fecha_ingreso", "placa", "marca", "modelo",
            "anio", "color", "asesor", "cedula_asesor",
            "cedula_responsable", "nombre_responsable", "correo_responsable", "telefono_responsable",
            "condicion", "provincia", "canton", "distrito", "cedula_empresa", "nombre_empresa","cedula_estimacion","nombre_estimacion"
        ]


        form_data = {field: request.form.get(field, "").strip() for field in required_fields}
        for field, value in form_data.items():
            if not value:
                return jsonify({"error": f"El campo {field} está vacío."}), 400

        aviso = form_data["aviso"]
        consecutivo = form_data["consecutivo"]
        opcion = form_data["opcion"]
        cedula_cliente = format_number(form_data["cedula"], is_cedula=True)
        nombre_cliente = form_data["nombre"]
        telefono_cliente = format_number(form_data["telefono"])
        correo_cliente = form_data["correo"]
        fecha_evento = form_data["fecha_evento"]
        fecha_ingreso = form_data["fecha_ingreso"]
        placa = form_data["placa"]
        marca = form_data["marca"]
        modelo = form_data["modelo"]
        anio = form_data["anio"]
        color = form_data["color"]
        asesor = form_data["asesor"]
        cedula_asesor = format_number(form_data["cedula_asesor"], is_cedula=True)
        dia_evento, mes_evento, anio_evento = split_date(fecha_evento)
        dia_ingreso, mes_ingreso, anio_ingreso = split_date(fecha_ingreso)

        # Datos del responsable
        cedula_responsable = format_number(form_data["cedula_responsable"], is_cedula=True)
        nombre_responsable = form_data["nombre_responsable"]
        correo_responsable = form_data["correo_responsable"]
        telefono_responsable = format_number(form_data["telefono_responsable"])
        
        cedula_estimacion = format_number(form_data["cedula_estimacion"], is_cedula=True)
        nombre_estimacion = form_data["nombre_estimacion"]
        
        # Datos de ubicación
        provincia = form_data["provincia"]
        canton = form_data["canton"]
        distrito = form_data["distrito"]
        
        # Datos de la empresa (si aplica)
        cedula_empresa = format_number(form_data["cedula_empresa"], is_cedula=True)
        nombre_empresa = form_data["nombre_empresa"]
        
        nombre_responsable = form_data["nombre_responsable"]
        correo_responsable = form_data["correo_responsable"]
        telefono_responsable = format_number(form_data["telefono_responsable"])

        # Obtener la fecha actual para el nombre del archivo
        current_date = datetime.now().strftime("%Y-%m-%d")
        sanitized_name = "".join([c if c.isalnum() or c in " ._-()" else "_" for c in nombre_cliente])

        save_path = os.getenv("UPLOAD_FOLDER", "/opt/render/project/files/WABEDOCS")
        os.makedirs(save_path, exist_ok=True)

        case_number_folder = os.path.join(save_path, f"25-{form_data['consecutivo']}")
        os.makedirs(case_number_folder, exist_ok=True)

        # ✅ 4️⃣ Definir rutas de salida para PDFs
        temp_pdf1_path = os.path.join(case_number_folder, "temp_valoracion.pdf")
        temp_pdf2_path = os.path.join(case_number_folder, "temp_estimacion.pdf")
        output_pdf1_path = os.path.join(case_number_folder, f"{form_data['nombre']}_valoracion.pdf")
        output_pdf2_path = os.path.join(case_number_folder, f"{form_data['nombre']}_estimacion.pdf")

       
        # --- Generar Primer PDF (Valoración) ---
        c1 = canvas.Canvas(temp_pdf1_path, pagesize=letter)
        c1.setFont("Helvetica-Bold", 50)
        c1.drawString(430, 650, f"{consecutivo}")
        c1.setFont("Helvetica-Bold", 22)
        c1.drawString(140, 550, f"{placa}")
        c1.setFont("Helvetica-Bold", 12)
        c1.drawString(140, 605, f"{aviso}")
        c1.drawString(445, 605, f"INS")
        c1.drawString(450, 550, f"{opcion}")
        c1.drawString(380, 480, f"{cedula_cliente}")
        c1.drawString(75, 480, f"{nombre_cliente}")
        c1.drawString(420, 525, f"{fecha_evento}")
        c1.drawString(185, 525, f"{fecha_ingreso}")
        c1.drawString(85, 270, f"{marca}")
        c1.drawString(220, 270, f"{modelo}")
        c1.drawString(360, 270, f"{anio}")
        c1.drawString(425, 270, f"{color}")
        
        c1.drawString(130, 350, f"{provincia}")
        c1.drawString(130, 333, f"{canton}")
        c1.drawString(130, 315, f"{distrito}")

        c1.setFont("Helvetica-Bold", 9)
        c1.drawString(355, 580, f"{asesor}")

        # Incluir datos del responsable
        c1.setFont("Helvetica-Bold", 8)
        c1.drawString(85, 415, f"{nombre_responsable}")
        c1.setFont("Helvetica-Bold", 10)
        c1.drawString(300, 398, f"{telefono_responsable}")
        c1.drawString(115, 398, f"{cedula_responsable}")
        c1.drawString(300, 415, f"{correo_responsable}")
        c1.save()

        # --- Generar Segundo PDF (Estimación) ---
        c2 = canvas.Canvas(temp_pdf2_path, pagesize=letter)
        c2.setFont("Helvetica-Bold", 10)
        c2.drawString(81, 678, f"{placa}")
        c2.drawString(435, 678, f"{aviso}")
        c2.setFont("Helvetica", 10)
        
        c2.drawString(380, 650, f"{cedula_estimacion}")
        c2.drawString(45, 650, f"{nombre_estimacion}")
        
        c2.drawString(500, 650, f"{telefono_cliente}")
        c2.drawString(105, 625, f"{correo_cliente}")
        
        # Fecha de eventos
        c2.drawString(60, 440, f"{dia_evento}")
        c2.drawString(120, 440, f"{mes_evento}")
        c2.drawString(180, 440, f"{anio_evento}")
        
        c2.drawString(442, 142, f"{dia_ingreso}")
        c2.drawString(495, 142, f"{mes_ingreso}")
        c2.drawString(550, 142, f"{anio_ingreso}")
        
        
        c2.drawString(70, 565, f"{cedula_empresa}")
        c2.drawString(145, 565, f"{nombre_empresa}")

        # Agregar condición
        condicion = form_data["condicion"]
        c2.setFont("Helvetica", 10)
        c2.drawString(40, 600, f"{condicion}")

        # Opciones de repuestos
        repuestos = {
            "nuevos_originales": "X" if request.form.get("nuevos_originales") == "on" else "",
            "genericos": "X" if request.form.get("genericos") == "on" else "",
            "usados_originales": "X" if request.form.get("usados_originales") == "on" else ""
        }

        c2.drawString(40, 325, repuestos["nuevos_originales"])
        c2.drawString(170, 325, repuestos["genericos"])
        c2.drawString(265, 325, repuestos["usados_originales"])

        c2.setFont("Helvetica-Bold", 9)
        c2.drawString(45, 168, f"{asesor}")
        c2.drawString(460, 168, f"{cedula_asesor}")
        
        c2.drawString(79, 479, f"WABE CARROCERIA Y PINTURA S.A.")
        c2.drawString(425, 479, f"3-101-085331")

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
