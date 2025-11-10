"""
Configurações globais do sistema
"""
import os

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'financas.json')

# Criar diretório de dados se não existir
os.makedirs(DATA_DIR, exist_ok=True)

# Categorias padrão
DEFAULT_CATEGORIES = {
    'receita': ['Salário', 'Freelance', 'Investimentos', 'Outros Ganhos'],
    'despesa': ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 
                'Educação', 'Lazer', 'Contas', 'Compras', 'Outros Gastos']
}

# Configurações de exibição
CURRENCY_SYMBOL = 'R$'
DATE_FORMAT = '%d/%m/%Y'
DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

# Limites
MAX_TRANSACTIONS_DISPLAY = 50
CHART_BAR_LENGTH = 50