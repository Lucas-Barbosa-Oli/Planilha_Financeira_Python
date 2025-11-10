"""
Gerenciador de Categorias
"""
from typing import Dict, List, Optional
from config import DEFAULT_CATEGORIES


class CategoryManager:
    """Gerencia categorias de receitas e despesas"""
    
    def __init__(self, categories: Optional[Dict[str, List[str]]] = None):
        # CORREÇÃO: Se None, usa cópia das categorias padrão
        if categories is None:
            self.categories = {
                'receita': DEFAULT_CATEGORIES['receita'].copy(),
                'despesa': DEFAULT_CATEGORIES['despesa'].copy()
            }
        else:
            self.categories = categories
    
    def get_categories(self, tipo: str) -> List[str]:
        """Retorna categorias de um tipo específico"""
        return self.categories.get(tipo, [])
    
    def add_category(self, tipo: str, nome: str) -> bool:
        """Adiciona nova categoria"""
        if tipo not in self.categories:
            return False
        
        if nome not in self.categories[tipo]:
            self.categories[tipo].append(nome)
            return True
        return False
    
    def remove_category(self, tipo: str, nome: str) -> bool:
        """Remove categoria"""
        if tipo in self.categories and nome in self.categories[tipo]:
            self.categories[tipo].remove(nome)
            return True
        return False
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Retorna todas as categorias"""
        return self.categories.copy()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return self.categories
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CategoryManager':
        """Cria instância a partir de dicionário"""
        return cls(categories=data)