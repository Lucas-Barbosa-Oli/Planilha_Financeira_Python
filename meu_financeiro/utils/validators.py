"""
Validadores de entrada
"""
from datetime import datetime
from config import DATE_FORMAT


def validate_date(date_str: str) -> bool:
    """Valida formato de data"""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def validate_value(value_str: str) -> tuple[bool, float]:
    """Valida e converte valor monetário"""
    try:
        value = float(value_str.replace(',', '.'))
        if value <= 0:
            return False, 0
        return True, value
    except ValueError:
        return False, 0


def validate_tipo(tipo: str) -> bool:
    """Valida tipo de transação"""
    return tipo in ['receita', 'despesa']


def validate_non_empty(text: str) -> bool:
    """Valida se texto não está vazio"""
    return bool(text.strip())