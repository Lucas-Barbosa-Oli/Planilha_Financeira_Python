"""
Formatadores de dados
"""
from datetime import datetime
from typing import Optional
from config import CURRENCY_SYMBOL, DATE_FORMAT, DATETIME_FORMAT


def format_currency(value: float, show_symbol: bool = True) -> str:
    """Formata valor monetário para padrão brasileiro"""
    formatted = f"{value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    return f"{CURRENCY_SYMBOL} {formatted}" if show_symbol else formatted


def format_date(date_str: str, input_format: Optional[str] = None) -> str:
    """Formata data para exibição"""
    # CORREÇÃO: Tratamento correto do input_format None
    if input_format is not None:
        date_obj = datetime.strptime(date_str, input_format)
    else:
        date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime(DATE_FORMAT)


def format_datetime(datetime_str: str) -> str:
    """Formata data e hora para exibição"""
    dt_obj = datetime.fromisoformat(datetime_str)
    return dt_obj.strftime(DATETIME_FORMAT)


def create_progress_bar(value: float, max_value: float, length: int = 50, 
                       char: str = '█') -> str:
    """Cria barra de progresso ASCII"""
    if max_value == 0:
        return ''
    
    filled_length = int(length * value / max_value)
    return char * filled_length