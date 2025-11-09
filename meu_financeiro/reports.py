# reports.py
from datetime import datetime
from collections import defaultdict, OrderedDict
import statistics

def moving_average(values, window=3):
    """Calcula média móvel simples sobre a lista de valores (lista pode ser vazia)."""
    if not values or window <= 0:
        return []
    ma = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        window_vals = values[start:i+1]
        ma.append(sum(window_vals) / len(window_vals))
    return ma

def monthly_accumulated(transactions):
    """
    Retorna OrderedDict mês-> {'receitas': x, 'despesas': y, 'saldo': z}
    mês formatado como 'YYYY-MM'
    """
    monthly = {}
    for t in transactions:
        try:
            dt = datetime.fromisoformat(t['data'])
        except Exception:
            # pular registros inválidos
            continue
        key = dt.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {'receitas': 0.0, 'despesas': 0.0}
        if t['tipo'] == 'receita':
            monthly[key]['receitas'] += t['valor']
        else:
            monthly[key]['despesas'] += t['valor']
    # ordenar por mês asc
    ordered = OrderedDict(sorted(monthly.items()))
    # adicionar saldo
    for k, v in ordered.items():
        v['saldo'] = v['receitas'] - v['despesas']
    return ordered

def top_categories(transactions, top_n=5):
    """Retorna lista de tuplas (categoria, total_despesas) ordenada desc. Considera somente despesas."""
    totals = {}
    for t in transactions:
        if t['tipo'] != 'despesa':
            continue
        cat = t.get('categoria') or 'Sem Categoria'
        totals[cat] = totals.get(cat, 0.0) + t['valor']
    sorted_cats = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_cats[:top_n]

def expenses_time_series(transactions, period='monthly'):
    """Retorna série temporal de despesas por mês (mapeamento YYYY-MM -> valor)."""
    monthly = monthly_accumulated(transactions)
    # transformar OrderedDict em listas
    months = list(monthly.keys())
    values = [monthly[m]['despesas'] for m in months]
    return months, values
