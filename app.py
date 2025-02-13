from flask import Flask, jsonify, request, render_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime
import subprocess
import sys
from flask import send_file
import tkinter as tk
from tkinter import filedialog



app = Flask(__name__)

@app.route('/verificar_ruta', methods=['GET'])
def verificar_ruta():
    ruta = "P:\\INS"  # Ruta a validar
    if os.path.exists(ruta):  # Verifica si la ruta existe
        return jsonify({"exists": True, "message": "✔ La ruta P:\\INS está disponible."})
    else:
        return jsonify({"exists": False, "message": "⚠ La ruta P:\\INS no está disponible."})


# Función para manejar rutas correctamente en PyInstaller
def resource_path(relative_path):
    """Retorna la ruta absoluta para PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app.template_folder = resource_path("templates")
app.static_folder = resource_path("static")



def split_date(date_str):
    """Divide una fecha en día, mes y año."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return " ", " ", " "


# Función para formatear cédulas y teléfonos
def format_number(value, is_cedula=False):
    """Formatea un número de teléfono, cédula física, cédula jurídica o DIMEX con guiones cuando corresponde."""
    
    # Si el valor es None o vacío, devolverlo tal cual
    if not value:
        return value

    # Eliminar espacios y verificar si es un número válido
    value = value.strip()
    if not value.isdigit():
        return ""

    if is_cedula:
        # Cédula Física: 9 dígitos -> X-XXXX-XXXX
        if len(value) == 9:
            return f"{value[0]}-{value[1:5]}-{value[5:]}"
        
        # Cédula Jurídica: 10 dígitos -> X-XXX-XXXXXX
        elif len(value) == 10:
            return f"{value[:1]}-{value[1:4]}-{value[4:]}"
        
        # DIMEX: 11 o 12 dígitos -> Se deja sin formato
        elif len(value) in [11, 12]:
            return value  # Se mantiene "corrida"
        
        else:
            return "Cédula inválida"  # Error de longitud

    else:
        # Validación de teléfono: 8 dígitos -> XXXX-XXXX
        if len(value) == 8:
            return f"{value[:4]}-{value[4:]}"
        else:
            return "Teléfono inválido"


ruta_guardado = os.path.join(os.path.expanduser("~"), "Desktop", "WABEDOCS")

@app.route("/seleccionar_carpeta")
def seleccionar_carpeta():
    try:
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana de Tkinter
        folder_selected = filedialog.askdirectory()  # Abre el selector de carpetas

        if folder_selected:  
            return jsonify({"path": folder_selected})  # Retorna la ruta de la carpeta
        else:
            return jsonify({"path": None})  # Si no se selecciona, retorna None

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/set_save_path", methods=["POST"])
def set_save_path():
    global ruta_guardado
    data = request.json
    nueva_ruta = data.get("path", "").strip()

    if os.path.exists(nueva_ruta):  # Validar si la carpeta existe
        ruta_guardado = nueva_ruta
        return jsonify({"message": f"✅ Ruta guardada en: {ruta_guardado}"})
    else:
        return jsonify({"message": "⚠️ Error: La ruta no existe."}), 400

# Asegurar que la carpeta de guardado exista
os.makedirs(ruta_guardado, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return jsonify({"message": "Servidor Flask activo"})

@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        # Verifica si los campos están presentes
        required_fields = [
            "aviso", "consecutivo", "opcion", "cedula", "nombre", "telefono",
            "correo", "fecha_evento", "fecha_ingreso", "placa", "marca", "modelo",
            "anio", "color", "asesor", "cedula_asesor",
            "cedula_responsable", "nombre_responsable", "correo_responsable", "telefono_responsable",
            "condicion", "provincia", "canton", "distrito", "cedula_empresa", "nombre_empresa","cedula_estimacion","nombre_estimacion"
        ]

        form_data = {}
        for field in required_fields:
            value = request.form.get(field)
            if not value:
                return f"Error: El campo {field} está vacío o no se ha enviado.", 400
            form_data[field] = value
            
  # Recibir los datos y formatear números
       
  
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

        # Crear una carpeta con el número de caso
        # Obtener la ruta del escritorio del usuario actual en Windows
        desktop_path = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

# Crear la carpeta en el escritorio con el número de caso

        case_number_folder = os.path.join(ruta_guardado, f"25-{consecutivo}")

        os.makedirs(case_number_folder, exist_ok=True)
        

        # Rutas de salida para los PDFs
        temp_pdf1_path = os.path.join(case_number_folder, "temp_valoracion.pdf")
        temp_pdf2_path = os.path.join(case_number_folder, "temp_estimacion.pdf")
             
        output_pdf1_path = os.path.join(case_number_folder, f"{sanitized_name}_{current_date}_valoracion.pdf")
        output_pdf2_path = os.path.join(case_number_folder, f"{sanitized_name}_{current_date}_estimacion.pdf")
        

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

       
        # --- Combinar los PDFs temporales con las plantillas ---
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

        # Obtener la ruta correcta para las plantillas PDF
        VALORACION_PDF_PATH = resource_path("pdfs/VALORACION.pdf")
        ESTIMACION_PDF_PATH = resource_path("pdfs/ESTIMACION.pdf")

        combine_pdfs(VALORACION_PDF_PATH, temp_pdf1_path, output_pdf1_path)
        combine_pdfs(ESTIMACION_PDF_PATH, temp_pdf2_path, output_pdf2_path)

       

        # Limpiar archivos temporales
        os.remove(temp_pdf1_path)
        os.remove(temp_pdf2_path)
     
        # Responder con los archivos generados
        subprocess.Popen([output_pdf1_path], shell=True)  # Abre el primer PDF
        subprocess.Popen([output_pdf2_path], shell=True)  # Abre el segundo PDF

        return "",204

    except Exception as e:
        print(f"Error al abrir los PDFs: {e}")
        return "", 500  # Devuelve un error sin mostrarlo en el frontend


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
