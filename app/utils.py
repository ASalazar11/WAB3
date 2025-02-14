from datetime import datetime

def split_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return " ", " ", " "

def format_number(value, is_cedula=False):
    if not value or not value.isdigit():
        return value
    if is_cedula and len(value) == 9:
        return f"{value[0]}-{value[1:5]}-{value[5:]}"
    return value
