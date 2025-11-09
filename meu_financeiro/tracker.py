# tracker.py
from datetime import datetime
from utils import load_json, save_json, ensure_dirs, DEFAULT_FILENAME, format_money
from reports import moving_average, monthly_accumulated, top_categories, expenses_time_series
import os

class FinanceTracker:
    def __init__(self, filename=None):
        ensure_dirs()
        self.filename = filename or DEFAULT_FILENAME
        data = load_json(self.filename)
        self.transactions = data.get('transactions', [])
        # categorias padrão (se quiser, podem ser carregadas do arquivo)
        default_categories = {
            'receita': ['Salário', 'Freelance', 'Investimentos', 'Outros Ganhos'],
            'despesa': ['Alimentação', 'Transporte', 'Moradia', 'Saúde',
                        'Educação', 'Lazer', 'Contas', 'Compras', 'Outros Gastos']
        }
        # mesclar categorias salvas com padrão
        file_cats = data.get('categories', {})
        self.categories = default_categories
        for k, v in file_cats.items():
            if k in self.categories:
                # adicionar sem duplicar
                for item in v:
                    if item not in self.categories[k]:
                        self.categories[k].append(item)
            else:
                self.categories[k] = v
        self.last_updated = data.get('last_updated')

    # ---------- helpers ----------
    def _next_id(self):
        return max((t.get('id', 0) for t in self.transactions), default=0) + 1

    def _save(self):
        payload = {
            'transactions': self.transactions,
            'categories': self.categories,
            'last_updated': datetime.now().isoformat()
        }
        save_json(payload, path=self.filename)

    # ---------- CRUD ----------
    def add_transaction(self, tipo, descricao, categoria, valor, data_iso=None):
        if not data_iso:
            data_iso = datetime.now().isoformat()
        tx = {
            'id': self._next_id(),
            'tipo': tipo,
            'categoria': categoria,
            'descricao': descricao,
            'valor': round(float(valor), 2),
            'data': data_iso,
            'criado_em': datetime.now().isoformat()
        }
        self.transactions.append(tx)
        self._save()
        return tx

    def list_transactions(self, ordered_desc=True):
        return sorted(self.transactions, key=lambda x: x.get('data', ''), reverse=ordered_desc)

    def get_transaction(self, tx_id):
        return next((t for t in self.transactions if t.get('id') == tx_id), None)

    def edit_transaction(self, tx_id, **fields):
        t = self.get_transaction(tx_id)
        if not t:
            return False
        # atualizar somente campos presentes
        for k, v in fields.items():
            if k in t and v is not None:
                if k == 'valor':
                    t[k] = round(float(v), 2)
                else:
                    t[k] = v
        self._save()
        return True

    def delete_transaction(self, tx_id):
        t = self.get_transaction(tx_id)
        if not t:
            return False
        self.transactions.remove(t)
        self._save()
        return True

    def clear_transactions(self):
        self.transactions = []
        self._save()

    # ---------- Reports/analyses ----------
    def compute_balance(self):
        receitas = sum(t['valor'] for t in self.transactions if t['tipo'] == 'receita')
        despesas = sum(t['valor'] for t in self.transactions if t['tipo'] == 'despesa')
        return receitas, despesas, receitas - despesas

    def monthly_summary(self):
        """Retorna OrderedDict com acumulado mensal (receitas, despesas, saldo)."""
        return monthly_accumulated(self.transactions)

    def top5_categories(self):
        return top_categories(self.transactions, top_n=5)

    def moving_average_expenses(self, window=3):
        months, values = expenses_time_series(self.transactions)
        ma = moving_average(values, window=window)
        return months, values, ma

    # ---------- Export helpers ----------
    def export_csv(self, filepath):
        # cria CSV simples
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("ID;Data;Tipo;Categoria;Descricao;Valor\n")
            for t in sorted(self.transactions, key=lambda x: x['data']):
                data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
                valor_fmt = f"{t['valor']:.2f}".replace('.', ',')
                line = f"{t['id']};{data_fmt};{t['tipo']};{t['categoria']};{t['descricao']};{valor_fmt}\n"
                f.write(line)

    def export_pdf(self, filepath):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            raise RuntimeError("reportlab não está instalado. Rode: pip install reportlab")
        c = canvas.Canvas(filepath, pagesize=A4)
        largura, altura = A4
        c.setFont("Helvetica", 10)
        y = altura - 40
        c.drawString(40, y, "Relatório de Transações")
        y -= 20
        headers = "ID | Data | Tipo | Categoria | Descrição | Valor"
        c.drawString(40, y, headers)
        y -= 20
        for t in sorted(self.transactions, key=lambda x: x['data']):
            data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
            linha = f"{t['id']} | {data_fmt} | {t['tipo']} | {t['categoria']} | {t['descricao'][:30]} | R$ {t['valor']:.2f}"
            c.drawString(40, y, linha)
            y -= 14
            if y < 60:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = altura - 40
        c.save()
