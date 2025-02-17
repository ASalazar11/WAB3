import sys
import io
import zipfile
from flask import jsonify, request, send_file
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.utils import format_number, split_date
from PyPDF2 import PdfReader, PdfWriter


def merge_pdfs(template_pdf_path, generated_pdf):
    output_buffer = io.BytesIO()
    writer = PdfWriter()

    # Leer la plantilla PDF desde el archivo
    template_reader = PdfReader(template_pdf_path)

    # Cargar la página de la plantilla sin modificarla
    template_page = template_reader.pages[0]  

    # Cargar el PDF generado en memoria
    generated_pdf.seek(0)
    generated_reader = PdfReader(generated_pdf)

    # Fusionar la plantilla con el PDF generado
    template_page.merge_page(generated_reader.pages[0])

    # Agregar la página fusionada al nuevo PDF
    writer.add_page(template_page)

    # Guardar el PDF final en memoria
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer


def generate_pdf(request):
    try:
        # ✅ 1️⃣ Verificar que todos los datos requeridos están presentes
        required_fields = [
            "aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono",
            "correo", "fecha_evento", "fecha_ingreso", "placa", "marca", "modelo",
            "anio", "color", "asesor", "cedula_asesor",
            "cedula_responsable", "nombre_responsable", "correo_responsable", "telefono_responsable",
            "condicion", "provincia", "canton", "distrito", "cedula_empresa", "nombre_empresa",
            "cedula_estimacion", "nombre_estimacion",
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
        
        #Segundas Personas Juridicas 
        CedulaJuridica2 = form_data["cedula_juridico_2"]
        NombreJuridica2 = form_data["nombre_juridico_2"]

        # Datos de ubicación
        provincia = form_data["provincia"]
        canton = form_data["canton"]
        distrito = form_data["distrito"]

        # Datos de la empresa (si aplica)
      
       # Datos de la empresa (si aplica)
        cedula_empresa = form_data.get("cedula_empresa", "").strip()
        nombre_empresa = form_data.get("nombre_empresa", "").strip()

        # Si están vacíos, se asigna "N/A" en lugar de None o string vacío
        cedula_empresa = format_number(form_data.get("cedula_empresa", ""), is_cedula=True)
        
        nombre_empresa = form_data.get("nombre_empresa")

        # Obtener la fecha actual para el nombre del archivo
        consecutivo_prefijo = f"25-{form_data['consecutivo']}"
        sanitized_name = "".join([c if c.isalnum() or c in " ._-()" else "_" for c in nombre_cliente])


        # ✅ 2️⃣ Cargar las plantillas
        VALORACION_PDF_PATH = "pdfs/VALORACION.pdf"
        ESTIMACION_PDF_PATH = "pdfs/ESTIMACION.pdf"

        # ✅ 3️⃣ Generar Primer PDF (Valoración)
        pdf1_buffer = io.BytesIO()
        c1 = canvas.Canvas(pdf1_buffer, pagesize=letter)

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
        
        if form_data.get("nombre_juridico_2", "").strip() != ".":
            c1.drawString(380,500,f"{CedulaJuridica2}")
            c1.drawString(75,500,f"{NombreJuridica2}")
        

        # Incluir datos del responsable
        c1.setFont("Helvetica-Bold", 8)
        c1.drawString(85, 415, f"{nombre_responsable}")
        c1.setFont("Helvetica-Bold", 10)
        c1.drawString(300, 398, f"{telefono_responsable}")
        c1.drawString(115, 398, f"{cedula_responsable}")
        c1.drawString(300, 415, f"{correo_responsable}")

        c1.save()
        pdf1_buffer.seek(0)

        # Fusionar con la plantilla
        pdf1_final = merge_pdfs(VALORACION_PDF_PATH, pdf1_buffer)

        # ✅ 4️⃣ Generar Segundo PDF (Estimación)
        pdf2_buffer = io.BytesIO()
        c2 = canvas.Canvas(pdf2_buffer, pagesize=letter)

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
        
        if form_data.get("nombre_empresa", "").strip() != ".":
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
        pdf2_buffer.seek(0)

        # Fusionar con la plantilla
        pdf2_final = merge_pdfs(ESTIMACION_PDF_PATH, pdf2_buffer)

        # ✅ 5️⃣ Enviar los archivos en un ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(f"{consecutivo_prefijo}_VALORACION_{sanitized_name}.pdf", pdf1_final.getvalue())
            zip_file.writestr(f"{consecutivo_prefijo}_ESTIMACION_{sanitized_name}.pdf", pdf2_final.getvalue())


        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{consecutivo_prefijo}.zip"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
