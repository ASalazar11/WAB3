from datetime import datetime

def split_date(date_str):
    """Divide una fecha en día, mes y año. Retorna espacios vacíos si la fecha no es válida."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return " ", " ", " "  # Si la fecha no es válida, devolver espacios

def format_number(value, is_cedula=False,genera_vacio=False):
    """Formatea un número de teléfono o cédula con guiones según corresponda."""
    
    if not value or not value.strip().isdigit():
        return " "  # 🔹 Mensaje uniforme para valores no numéricos

    value = value.strip()
    
    if genera_vacio and not value:
        return " "

    if is_cedula:
        if len(value) == 9:  # Cédula física
            return f"{value[0]}-{value[1:5]}-{value[5:]}"
        elif len(value) == 10:  # Cédula jurídica
            return f"{value[:1]}-{value[1:4]}-{value[4:]}"
        elif len(value) in [11, 12]:  # DIMEX
            return value
        return " "
    
    # Teléfono
    if len(value) == 8:
        return f"{value[:4]}-{value[4:]}"
    return " "
