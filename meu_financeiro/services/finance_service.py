"""
Serviço de lógica financeira
"""
from typing import List, Dict, Optional
from datetime import datetime
import statistics
from models import Transaction, CategoryManager


class FinanceService:
    """Gerencia operações financeiras"""
    
    def __init__(self, transactions: List[Transaction], 
                 categories: CategoryManager):
        self.transactions = transactions
        self.categories = categories
    
    def add_transaction(self, tipo: str, categoria: str, descricao: str,
                       valor: float, data: str) -> Transaction:
        """Adiciona nova transação"""
        new_id = max([t.id for t in self.transactions], default=0) + 1
        
        transaction = Transaction(
            id=new_id,
            tipo=tipo,
            categoria=categoria,
            descricao=descricao,
            valor=valor,
            data=data
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def update_transaction(self, trans_id: int, **kwargs) -> bool:
        """Atualiza transação existente"""
        transaction = self.get_transaction_by_id(trans_id)
        
        if not transaction:
            return False
        
        for key, value in kwargs.items():
            if hasattr(transaction, key) and value is not None:
                setattr(transaction, key, value)
        
        return True
    
    def delete_transaction(self, trans_id: int) -> bool:
        """Remove transação"""
        transaction = self.get_transaction_by_id(trans_id)
        
        if transaction:
            self.transactions.remove(transaction)
            return True
        
        return False
    
    def get_transaction_by_id(self, trans_id: int) -> Optional[Transaction]:
        """Busca transação por ID"""
        return next((t for t in self.transactions if t.id == trans_id), None)
    
    def filter_by_period(self, start: datetime, end: datetime) -> List[Transaction]:
        """Filtra transações por período"""
        return [
            t for t in self.transactions
            if start <= t.get_date_obj() <= end
        ]
    
    def filter_by_description(self, term: str) -> List[Transaction]:
        """Filtra por descrição"""
        term_lower = term.lower()
        return [
            t for t in self.transactions
            if term_lower in t.descricao.lower()
        ]
    
    def filter_by_category(self, category: str) -> List[Transaction]:
        """Filtra por categoria"""
        return [t for t in self.transactions if t.categoria == category]
    
    def filter_by_value_range(self, min_val: float, 
                             max_val: float) -> List[Transaction]:
        """Filtra por faixa de valor"""
        return [
            t for t in self.transactions
            if min_val <= t.valor <= max_val
        ]
    
    def calculate_summary(self, transactions: Optional[List[Transaction]] = None) -> Dict:
        """Calcula resumo financeiro"""
        # CORREÇÃO: Se None, usa todas as transações
        trans = transactions if transactions is not None else self.transactions
        
        receitas = [t for t in trans if t.tipo == 'receita']
        despesas = [t for t in trans if t.tipo == 'despesa']
        
        total_receitas = sum(t.valor for t in receitas)
        total_despesas = sum(t.valor for t in despesas)
        saldo = total_receitas - total_despesas
        
        return {
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo': saldo,
            'num_receitas': len(receitas),
            'num_despesas': len(despesas),
            'total_transactions': len(trans)
        }
    
    def calculate_by_category(self, transactions: Optional[List[Transaction]] = None,
                             tipo: str = 'despesa') -> Dict[str, float]:
        """Calcula total por categoria"""
        # CORREÇÃO: Se None, usa todas as transações
        trans = transactions if transactions is not None else self.transactions
        filtered = [t for t in trans if t.tipo == tipo]
        
        category_totals = {}
        for t in filtered:
            category_totals[t.categoria] = category_totals.get(t.categoria, 0) + t.valor
        
        return dict(sorted(category_totals.items(), 
                          key=lambda x: x[1], reverse=True))
    
    def get_statistics(self, transactions: Optional[List[Transaction]] = None) -> Dict:
        """Calcula estatísticas"""
        # CORREÇÃO: Se None, usa todas as transações
        trans = transactions if transactions is not None else self.transactions
        
        if not trans:
            return {}
        
        receitas = [t.valor for t in trans if t.tipo == 'receita']
        despesas = [t.valor for t in trans if t.tipo == 'despesa']
        
        stats = {}
        
        if receitas:
            stats['media_receitas'] = statistics.mean(receitas)
            stats['maior_receita'] = max(receitas)
        
        if despesas:
            stats['media_despesas'] = statistics.mean(despesas)
            stats['maior_despesa'] = max(despesas)
            despesas_trans = [t for t in trans if t.tipo == 'despesa']
            stats['maior_despesa_obj'] = max(despesas_trans, 
                                            key=lambda x: x.valor)
        
        return stats
    
    def get_monthly_data(self, num_months: int = 12) -> List[Dict]:
        """Agrupa dados por mês"""
        monthly_data = {}
        
        for t in self.transactions:
            date = t.get_date_obj()
            month_key = date.strftime('%Y-%m')
            month_name = date.strftime('%b/%Y')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'name': month_name,
                    'receitas': 0.0,
                    'despesas': 0.0
                }
            
            if t.tipo == 'receita':
                monthly_data[month_key]['receitas'] += t.valor
            else:
                monthly_data[month_key]['despesas'] += t.valor
        
        sorted_months = sorted(monthly_data.items())[-num_months:]
        return [{'key': k, **v} for k, v in sorted_months]
    
    def get_all_transactions_sorted(self, reverse: bool = True) -> List[Transaction]:
        """Retorna transações ordenadas por data"""
        return sorted(self.transactions, 
                     key=lambda x: x.data, reverse=reverse)