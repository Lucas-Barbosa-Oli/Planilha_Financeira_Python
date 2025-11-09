# utils.py
import os
import json
from datetime import datetime
from shutil import copy2

DATA_DIR = "data"
EXPORTS_DIR = "exports"
DEFAULT_FILENAME = os.path.join(DATA_DIR, "financas.json")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_money(value):
    """Formata número para R$ com vírgula como separador decimal."""
    try:
        return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    except Exception:
        return f"R$ {value}"

def backup_file(path):
    """Cria um backup com timestamp do arquivo especificado."""
    if os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path}.{timestamp}.bak"
        try:
            copy2(path, backup_name)
        except Exception:
            # se backup falhar, ignoramos (não queremos interromper o fluxo)
            pass

def load_json(path=DEFAULT_FILENAME):
    """Carrega JSON do arquivo; retorna dict com chaves padrão se não existir."""
    ensure_dirs()
    if not os.path.exists(path):
        return {'transactions': [], 'categories': {}, 'last_updated': None}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # se falhar ao ler, retorna estrutura vazia
        return {'transactions': [], 'categories': {}, 'last_updated': None}

def save_json(obj, path=DEFAULT_FILENAME):
    """Salva JSON com backup automático."""
    ensure_dirs()
    # backup
    try:
        backup_file(path)
    except Exception:
        pass
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
