"""
Serviço de armazenamento de dados
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from config import DATA_FILE
from models import Transaction, CategoryManager


class StorageService:
    """Gerencia persistência de dados"""
    
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
    
    def load(self) -> tuple[List[Transaction], CategoryManager]:
        """Carrega dados do arquivo"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            transactions = [
                Transaction.from_dict(t) 
                for t in data.get('transactions', [])
            ]
            
            categories = CategoryManager.from_dict(
                data.get('categories', {})
            )
            
            return transactions, categories
            
        except FileNotFoundError:
            return [], CategoryManager()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return [], CategoryManager()
    
    def save(self, transactions: List[Transaction], 
             categories: CategoryManager) -> bool:
        """Salva dados no arquivo"""
        try:
            data = {
                'transactions': [t.to_dict() for t in transactions],
                'categories': categories.to_dict(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    def export_to_csv(self, transactions: List[Transaction], 
                      filename: str) -> bool:
        """Exporta transações para CSV"""
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                f.write("ID;Data;Tipo;Categoria;Descrição;Valor\n")
                
                for t in sorted(transactions, key=lambda x: x.data):
                    from utils import format_date, format_currency
                    data_fmt = format_date(t.data)
                    valor_fmt = format_currency(t.valor, show_symbol=False)
                    
                    f.write(f"{t.id};{data_fmt};{t.tipo};{t.categoria};"
                           f"{t.descricao};{valor_fmt}\n")
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar: {e}")
            return False