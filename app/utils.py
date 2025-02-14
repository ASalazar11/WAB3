from datetime import datetime
from datetime import datetime

def split_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return " ", " ", " "

def format_number(value, is_cedula=False):
    """Formatea un número de teléfono, cédula física, cédula jurídica o DIMEX con guiones cuando corresponde."""
    if not value:
        return value

    value = value.strip()
    if not value.isdigit():
        return ""

    if is_cedula:
        if len(value) == 9:
            return f"{value[0]}-{value[1:5]}-{value[5:]}"
        elif len(value) == 10:
            return f"{value[:1]}-{value[1:4]}-{value[4:]}"
        elif len(value) in [11, 12]:
            return value
        else:
            return "Cédula inválida"
    else:
        if len(value) == 8:
            return f"{value[:4]}-{value[4:]}"
        else:
            return "Teléfono inválido"
