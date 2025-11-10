"""
Modelo de Transação
"""
from datetime import datetime
from typing import Dict, Optional


class Transaction:
    """Representa uma transação financeira"""
    
    def __init__(self, id: int, tipo: str, categoria: str, 
                 descricao: str, valor: float, data: str, 
                 criado_em: Optional[str] = None):
        self.id = id
        self.tipo = tipo  # 'receita' ou 'despesa'
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor
        self.data = data  # ISO format
        self.criado_em = criado_em or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'valor': self.valor,
            'data': self.data,
            'criado_em': self.criado_em
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data['id'],
            tipo=data['tipo'],
            categoria=data['categoria'],
            descricao=data['descricao'],
            valor=data['valor'],
            data=data['data'],
            criado_em=data.get('criado_em')
        )
    
    def get_date_obj(self) -> datetime:
        """Retorna data como objeto datetime"""
        return datetime.fromisoformat(self.data)
    
    def __repr__(self):
        return f"Transaction(id={self.id}, tipo={self.tipo}, valor={self.valor})"