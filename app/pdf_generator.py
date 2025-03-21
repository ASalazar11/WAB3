import sys
import io
import zipfile
from flask import jsonify, request, send_file
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.utils import format_number, split_date
from PyPDF2 import PdfReader, PdfWriter

from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import legal
from datetime import datetime

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors

styles = getSampleStyleSheet()
justified_style = ParagraphStyle(
    'Justify',
    parent=styles['Normal'],
    alignment=TA_JUSTIFY,  
    fontSize=11,
    leading=14, 
    textColor=colors.black
)

def draw_wrapped_text(canvas, text, x, y, max_width):
    """
    Dibuja texto con saltos de línea automáticos dentro del PDF.
    """
    paragraph = Paragraph(text, justified_style)
    paragraph.wrapOn(canvas, max_width, 100)  
    canvas.setFillColor(colors.black)  
    paragraph.drawOn(canvas, x, y)

def formatear_fecha(fecha):
    """
    Convierte una fecha en formato 'YYYY-MM-DD' a '2 de febrero del 2025'
    """
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
        7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")  
    dia = fecha_dt.day
    mes = meses[fecha_dt.month]
    anio = fecha_dt.year
    
    return f"{dia} de {mes} del {anio}"

def merge_pdfs(template_pdf_path, generated_pdf):
    output_buffer = io.BytesIO()
    writer = PdfWriter()

    template_reader = PdfReader(template_pdf_path)

    template_page = template_reader.pages[0]  

    generated_pdf.seek(0)
    generated_reader = PdfReader(generated_pdf)

    template_page.merge_page(generated_reader.pages[0])

    writer.add_page(template_page)

    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer


def generate_pdf(request):
    try:
        required_fields = [
            "aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono",
            "correo", "fecha_evento", "fecha_ingreso", "placa", "marca", "modelo",
            "anio", "color", "asesor", "cedula_asesor",
            "cedula_responsable", "nombre_responsable", "correo_responsable", "telefono_responsable",
            "condicion", "provincia", "canton", "distrito", "cedula_empresa", "nombre_empresa",
            "cedula_estimacion", "nombre_estimacion","cedula_juridica_2","nombre_juridico_2"
        ]

        form_data = {field: request.form.get(field, "").strip() for field in required_fields}
        for field, value in form_data.items():
            if not value:
                return jsonify({"error": f"El campo {field} está vacío."}), 400
            
        

        checkboxes = {
            "noSeQueda": "X" if request.form.get("noSeQueda") == "on" else "",
            "check_opcion1": "X" if request.form.get("check_opcion1") == "on" else "",
            "check_opcion2": "X" if request.form.get("check_opcion2") == "on" else "",
        }


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

        cedula_responsable = format_number(form_data["cedula_responsable"], is_cedula=True)
        nombre_responsable = form_data["nombre_responsable"]
        correo_responsable = form_data["correo_responsable"]
        telefono_responsable = format_number(form_data["telefono_responsable"])
        cedula_estimacion = format_number(form_data["cedula_estimacion"], is_cedula=True)
        nombre_estimacion = form_data["nombre_estimacion"]
        
        #Segundas Personas Juridicas 
        # Obtener valores del formulario asegurando que no sean None
        CedulaJuridica2 = format_number(form_data.get("cedula_juridica_2", ".").strip(), is_cedula=True)
        NombreJuridica2 = form_data.get("nombre_juridico_2", ".").strip()

        # Datos de ubicación
        provincia = form_data["provincia"]
        canton = form_data["canton"]
        distrito = form_data["distrito"]

       # Datos de la empresa (si aplica)
        cedula_empresa = form_data.get("cedula_empresa", "").strip()
        nombre_empresa = form_data.get("nombre_empresa", "").strip()

        # Si están vacíos, se asigna "N/A" en lugar de None o string vacío
        cedula_empresa = format_number(form_data.get("cedula_empresa", ""), is_cedula=True)
        
        nombre_empresa = form_data.get("nombre_empresa")
        
        if consecutivo == ".": 
            consecutivo = placa
       
        consecutivo_prefijo = f"25-{consecutivo}"
        sanitized_name = "".join([c if c.isalnum() or c in " ._-()" else "_" for c in nombre_cliente])


        # ✅ 2️⃣ Cargar las plantillas
        VALORACION_PDF_PATH = "pdfs/VALORACION.pdf"
        ESTIMACION_PDF_PATH = "pdfs/ESTIMACION.pdf"
        PEJV_PDF_PATH = "pdfs/PEJV.pdf"
        PEFV_PDF_PATH = "pdfs/PEFV.pdf"
        VBF_PDF_PATH = "pdfs/VistoBuenoFisico.pdf"
        VBJ_PDF_PATH = "pdfs/VistoBuenoJuridico.pdf"
        

        # ✅ 3️⃣ Generar Primer PDF (Valoración)
        pdf1_buffer = io.BytesIO()
        c1 = canvas.Canvas(pdf1_buffer, pagesize=letter)
        
        if consecutivo == placa: 
            consecutivo = ""
        
        checkboxes = {
            "noSeQueda": "X"if request.form.get("noSeQueda") == "on" else "",
            "check_opcion1": "X" if request.form.get("check_opcion1", "off") == "on" else "",
            "check_opcion2": "X" if request.form.get("check_opcion2", "off") == "on" else "",
        }

        
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
 
        if checkboxes["noSeQueda"] == "X":
            c1.drawString(255, 235, f"Queda Reparando")
        
        c1.drawString(130, 350, f"{provincia}")
        c1.drawString(130, 333, f"{canton}")
        c1.drawString(130, 315, f"{distrito}")

        c1.setFont("Helvetica-Bold", 9)
        c1.drawString(355, 580, f"{asesor}")
        
        if form_data.get("cedula_juridica_2", "").strip() != ".":
            c1.setFont("Helvetica-Bold", 12)
            c1.drawString(380, 460, CedulaJuridica2)
            c1.drawString(75, 460, NombreJuridica2)

        

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
        
        pdf_pejv_buffer = io.BytesIO()
        c3 = canvas.Canvas(pdf_pejv_buffer, pagesize=legal)

        texto_pejv = f"""Quien suscribe, {nombre_estimacion}, portador de la cédula {cedula_estimacion}, como APODERADO GENERALÍSIMO SIN LÍMITE DE SUMA DE {nombre_empresa}, 
        cédula jurídica {cedula_empresa} en calidad de Asegurado del vehículo placa {placa} el PODERDANTE, otorgó PODER ESPECIAL de conformidad 
        con el artículo mil doscientos cincuenta y seis del Código Civil de la República de Costa Rica a favor de la señora Krisby Wabe Arce, mayor, 
        soltera, vecina de Curridabat, con número de cédula 1-112190411 y/o Mirkala Wabe Arce, mayor, soltera, vecina de Curridabat, con número de 
        cédula 1-10990472, y/o David Matamoros Rojas, mayor, casado, vecino de Cartago, con número de cédula 1-10650005, pudiendo actuar conjunta o 
        separadamente, funcionarios del taller Wabe, Carrocería y Pintura, Sociedad Anónima, cédula de persona jurídica 3-101-085331, en lo sucesivo 
        los APODERADOS, les faculto para que en mi representación realicen gestiones ante cualesquiera de las instalaciones o departamentos del 
        Instituto Nacional de Seguros."""
        fecha_ingreso_formateada = formatear_fecha(fecha_ingreso)
        texto_pejv2 = f"""Así mismo se encuentra facultado cualquiera de estos apoderados o todos en conjunto a interponer 
        cualquier recurso procedente, incluyendo recursos de revocatoria, apelación y solicitar el agotamiento de la vía administrativa, 
        en caso que el INS no indemnice el caso. Este poder especial sólo podrá ser revocado por el poderdante o mandatario a partir del momento 
        en que el apoderado haya recibido del Instituto Nacional de Seguros la indemnización total, que corresponde al total de la cuenta que ha 
        generado la reparación del (os) vehículo (s) aquí descrito (s) y referido (s), menos las deducciones registradas en la liquidación final 
        del reclamo. El poderdante renuncia a cualquier reclamo posterior. Lo antes aquí autorizado está relacionado al número de aviso de 
        accidente: CAS-{aviso}, vehículo {placa} De conformidad con todo lo anterior, firmo en San José, del día {fecha_ingreso_formateada}. 
        ES TODO ***** """    
        # Llamar a la función para dibujar el texto con saltos de línea automáticos
        draw_wrapped_text(c3, texto_pejv, 36, 790, 540)  # x=100, y=700, ancho máximo=400px
        
        draw_wrapped_text(c3, texto_pejv2, 36, 230, 540)
        
        c3.setFont("Helvetica-Bold", 14)
        c3.drawString(36, 145, f"{nombre_estimacion}")
        c3.drawString(95, 128, f"{cedula_estimacion}")

        # Guardar y posicionar el documento
        c3.save()
        pdf_pejv_buffer.seek(0)
        
        pdf3_final = merge_pdfs(PEJV_PDF_PATH, pdf_pejv_buffer)
        
        pdf_pefv_buffer = io.BytesIO()
        c4 = canvas.Canvas(pdf_pefv_buffer, pagesize=legal)

        texto_pefv = f"""Quien suscribe, {nombre_estimacion}, portador de la cédula {cedula_estimacion}, en calidad de PROPIETARIO del vehículo placa {placa}, otorgó PODER ESPECIAL de conformidad 
        con el artículo mil doscientos cincuenta y seis del Código Civil de la República de Costa Rica a favor de la señora Krisby Wabe Arce, mayor, 
        soltera, vecina de Curridabat, con número de cédula 1-112190411 y/o Mirkala Wabe Arce, mayor, soltera, vecina de Curridabat, con número de 
        cédula 1-10990472, y/o David Matamoros Rojas, mayor, casado, vecino de Cartago, con número de cédula 1-10650005, pudiendo actuar conjunta o 
        separadamente, funcionarios del taller Wabe, Carrocería y Pintura, Sociedad Anónima, cédula de persona jurídica 3-101-085331, en lo sucesivo 
        los APODERADOS, les faculto para que en mi representación realicen gestiones ante cualesquiera de las instalaciones o departamentos del 
        Instituto Nacional de Seguros."""
        
        fecha_ingreso_formateada = formatear_fecha(fecha_ingreso)
        
        texto_pefv2 = f"""Así mismo se encuentra facultado cualquiera de estos apoderados o todos en conjunto a interponer 
        cualquier recurso procedente, incluyendo recursos de revocatoria, apelación y solicitar el agotamiento de la vía administrativa, 
        en caso que el INS no indemnice el caso. Este poder especial sólo podrá ser revocado por el poderdante o mandatario a partir del momento 
        en que el apoderado haya recibido del Instituto Nacional de Seguros la indemnización total, que corresponde al total de la cuenta que ha 
        generado la reparación del (os) vehículo (s) aquí descrito (s) y referido (s), menos las deducciones registradas en la liquidación final 
        del reclamo. El poderdante renuncia a cualquier reclamo posterior. Lo antes aquí autorizado está relacionado al número de aviso de 
        accidente: CAS-{aviso}, vehículo {placa} De conformidad con todo lo anterior, firmo en San José, del día {fecha_ingreso_formateada}. 
        ES TODO ***** """    
        
        draw_wrapped_text(c4, texto_pefv, 36, 810, 540)  
        
        draw_wrapped_text(c4, texto_pefv2, 36, 230, 540)
        
        c4.setFont("Helvetica-Bold", 14)
        c4.drawString(36, 141, f"{nombre_cliente}")
        c4.drawString(95, 124, f"{cedula_cliente}")
        
        c4.save()
        pdf_pefv_buffer.seek(0)
        
        pdf4_final = merge_pdfs(PEFV_PDF_PATH, pdf_pefv_buffer)
        
        
        
        pdf_vbf_buffer = io.BytesIO()
        c5 = canvas.Canvas(pdf_vbf_buffer, pagesize=legal)

        texto_vbf = f"""Yo {nombre_cliente}, portador (a) de la cedula {cedula_cliente} en calidad de
        PROPIETARIA del vehículo placa {placa} según CAS {aviso} autorizo lo anterior 
        pues he recibido de ustedes la comunicación al detalle todas las 
        informaciones relacionadas con el proceso de avalúo y trámites ante el INS """
        
        fecha_ingreso_formateada = formatear_fecha(fecha_ingreso)
       
        draw_wrapped_text(c5, texto_vbf, 85, 395, 448)  
        
        c5.setFont("Helvetica-Bold", 11)
        c5.drawString(410, 660, f"{fecha_ingreso_formateada}")
        
        c5.drawString(85, 155, f"{nombre_cliente}")
        c5.drawString(133, 139, f"{cedula_cliente}")
        # Guardar y posicionar el documento
        c5.save()
        pdf_vbf_buffer.seek(0)
        pdf5_final = merge_pdfs(VBF_PDF_PATH, pdf_vbf_buffer)
        
        
        pdf_vbj_buffer = io.BytesIO()
        c6 = canvas.Canvas(pdf_vbj_buffer, pagesize=legal)

        texto_vbj = f"""Por este medio {nombre_estimacion}, portador de la cedula {cedula_estimacion}, como Apoderado de {nombre_empresa}, cedula jurídica 
        cedula {cedula_empresa} PROPIETARIO del vehículo placa {placa} según aviso de accidente CAS {aviso} , autorizo para que la indemnización de dicho
        vehículo sea girada a nombre de Wabe Carrocería y Pintura S.A., cédula jurídica número 3-101-085331  depositada en la cuenta 
        en colones número CR86012300130014399008 o en su defecto en la cuenta en dólares número CR21012300130014399014, ambas correspondientes al SCOTIABANK.
        A su vez manifiesto entera conformidad con la reparación realizada por el Taller WABE CARROCERIA Y PINTURA S.A."""
              
        draw_wrapped_text(c6, texto_vbj, 85, 380, 448)  
        
        c6.setFont("Helvetica-Bold", 11)
        c6.drawString(85, 186, f"{nombre_estimacion}")
        c6.drawString(140, 171, f"{cedula_estimacion}")
        # Guardar y posicionar el documento
        c6.save()
        pdf_vbj_buffer.seek(0)
        pdf6_final = merge_pdfs(VBJ_PDF_PATH, pdf_vbj_buffer)
        
        

        # ✅ 5️⃣ Enviar los archivos en un ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr(f"{consecutivo_prefijo}_VALORACION_{sanitized_name}.pdf", pdf1_final.getvalue())
            zip_file.writestr(f"{consecutivo_prefijo}_ESTIMACION_{sanitized_name}.pdf", pdf2_final.getvalue())

            if checkboxes["check_opcion1"] == "X":
                zip_file.writestr(f"{consecutivo_prefijo}_PoderEspecialJuridico_{sanitized_name}.pdf", pdf3_final.getvalue())
                zip_file.writestr(f"{consecutivo_prefijo}_VistoBuenoJuridico_{sanitized_name}.pdf", pdf6_final.getvalue())

            if checkboxes["check_opcion2"] == "X":
                zip_file.writestr(f"{consecutivo_prefijo}_PoderEspecialFisico_{sanitized_name}.pdf", pdf4_final.getvalue())
                zip_file.writestr(f"{consecutivo_prefijo}_VistoBuenoFisico_{sanitized_name}.pdf", pdf5_final.getvalue())


        zip_buffer.seek(0)  

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{consecutivo_prefijo}.zip"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
