"""
Sistema de Controle Financeiro Pessoal
Ponto de entrada da aplicação
"""

from services import FinanceService, StorageService
from views import TerminalView


def main():
    """Função principal"""
    # Inicializar serviços
    storage = StorageService()
    transactions, categories = storage.load()
    
    finance = FinanceService(transactions, categories)
    
    # Inicializar view
    view = TerminalView(finance, storage)
    
    # Executar aplicação
    view.run()


if __name__ == "__main__":
    main()