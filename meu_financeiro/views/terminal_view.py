"""
Interface de terminal (CLI)
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional
from models import Transaction
from services import FinanceService, StorageService
from utils import format_currency, format_date, validate_date, validate_value
from config import CHART_BAR_LENGTH


class TerminalView:
    """Interface do usuário via terminal"""
    
    def __init__(self, finance_service: FinanceService, 
                 storage_service: StorageService):
        self.finance = finance_service
        self.storage = storage_service
    
    def clear_screen(self):
        """Limpa tela"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Menu principal"""
        self.clear_screen()
        print("=" * 60)
        print("💰 SISTEMA DE CONTROLE FINANCEIRO PESSOAL 💰".center(60))
        print("=" * 60)
        print("\n1.  📝 Adicionar Transação")
        print("2.  📋 Listar Transações")
        print("3.  ✏️  Editar Transação")
        print("4.  🗑️  Deletar Transação")
        print("5.  📊 Resumo Financeiro")
        print("6.  📈 Gráfico Mensal")
        print("7.  🔍 Buscar Transações")
        print("8.  📁 Gerenciar Categorias")
        print("9.  💾 Exportar para CSV")
        print("10. 🚪 Sair")
        print("\n" + "=" * 60)
    
    def add_transaction(self):
        """Adiciona nova transação"""
        self.clear_screen()
        print("=" * 60)
        print("ADICIONAR NOVA TRANSAÇÃO".center(60))
        print("=" * 60)
        
        # Tipo
        print("\n1. Receita")
        print("2. Despesa")
        tipo_choice = input("\nEscolha o tipo (1-2): ").strip()
        
        tipo = 'receita' if tipo_choice == '1' else 'despesa' if tipo_choice == '2' else None
        if not tipo:
            print("✗ Opção inválida!")
            input("\nPressione ENTER...")
            return
        
        # Categoria
        categories = self.finance.categories.get_categories(tipo)
        print(f"\n--- Categorias de {tipo.upper()} ---")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        try:
            cat_idx = int(input(f"\nEscolha (1-{len(categories)}): ")) - 1
            categoria = categories[cat_idx]
        except (ValueError, IndexError):
            print("✗ Categoria inválida!")
            input("\nPressione ENTER...")
            return
        
        # Descrição
        descricao = input("\nDescrição: ").strip()
        if not descricao:
            print("✗ Descrição obrigatória!")
            input("\nPressione ENTER...")
            return
        
        # Valor
        valor_str = input("Valor (R$): ").strip()
        valid, valor = validate_value(valor_str)
        if not valid:
            print("✗ Valor inválido!")
            input("\nPressione ENTER...")
            return
        
        # Data
        data_input = input("Data (DD/MM/AAAA) ou ENTER para hoje: ").strip()
        if data_input:
            if not validate_date(data_input):
                print("✗ Data inválida!")
                input("\nPressione ENTER...")
                return
            data = datetime.strptime(data_input, '%d/%m/%Y').isoformat()
        else:
            data = datetime.now().isoformat()
        
        # Adicionar
        transaction = self.finance.add_transaction(tipo, categoria, descricao, valor, data)
        self.storage.save(self.finance.transactions, self.finance.categories)
        
        print(f"\n✓ {tipo.capitalize()} de {format_currency(valor)} adicionada!")
        input("\nPressione ENTER...")
    
    def list_transactions(self, transactions: Optional[List[Transaction]] = None):
        """Lista transações"""
        # CORREÇÃO: Tratamento correto do None
        self.clear_screen()
        
        if transactions is not None:
            trans = transactions
        else:
            trans = self.finance.get_all_transactions_sorted()
        
        if not trans:
            print("=" * 60)
            print("NENHUMA TRANSAÇÃO ENCONTRADA".center(60))
            print("=" * 60)
            input("\nPressione ENTER...")
            return
        
        print("=" * 100)
        print("LISTA DE TRANSAÇÕES".center(100))
        print("=" * 100)
        
        print(f"\n{'ID':<5} {'Data':<12} {'Tipo':<10} {'Categoria':<15} {'Descrição':<25} {'Valor':>15}")
        print("-" * 100)
        
        for t in trans:
            data_fmt = format_date(t.data)
            tipo_sym = '+' if t.tipo == 'receita' else '-'
            valor_fmt = f"{tipo_sym}{format_currency(t.valor)}"
            
            print(f"{t.id:<5} {data_fmt:<12} {t.tipo:<10} {t.categoria:<15} "
                  f"{t.descricao[:25]:<25} {valor_fmt:>15}")
        
        print("-" * 100)
        print(f"Total: {len(trans)} transações")
        input("\nPressione ENTER...")
    
    def edit_transaction(self):
        """Edita transação"""
        self.clear_screen()
        print("=" * 60)
        print("EDITAR TRANSAÇÃO".center(60))
        print("=" * 60)
        
        recent = self.finance.get_all_transactions_sorted()[:10]
        print("\nÚltimas transações:")
        for t in recent:
            print(f"ID {t.id}: {format_date(t.data)} - {t.descricao} - {format_currency(t.valor)}")
        
        try:
            trans_id = int(input("\nID para editar: "))
            transaction = self.finance.get_transaction_by_id(trans_id)
            
            if not transaction:
                print("✗ Não encontrada!")
                input("\nPressione ENTER...")
                return
            
            print(f"\n--- Editando: {transaction.descricao} ---")
            print("(ENTER para manter atual)")
            
            updates = {}
            
            new_desc = input(f"Descrição [{transaction.descricao}]: ").strip()
            if new_desc:
                updates['descricao'] = new_desc
            
            new_val = input(f"Valor [{transaction.valor:.2f}]: ").strip()
            if new_val:
                valid, valor = validate_value(new_val)
                if valid:
                    updates['valor'] = valor
            
            new_date = input(f"Data [{format_date(transaction.data)}]: ").strip()
            if new_date and validate_date(new_date):
                updates['data'] = datetime.strptime(new_date, '%d/%m/%Y').isoformat()
            
            if self.finance.update_transaction(trans_id, **updates):
                self.storage.save(self.finance.transactions, self.finance.categories)
                print("\n✓ Atualizada!")
            else:
                print("\n✗ Erro ao atualizar!")
                
        except ValueError:
            print("✗ ID inválido!")
        
        input("\nPressione ENTER...")
    
    def delete_transaction(self):
        """Deleta transação"""
        self.clear_screen()
        print("=" * 60)
        print("DELETAR TRANSAÇÃO".center(60))
        print("=" * 60)
        
        recent = self.finance.get_all_transactions_sorted()[:10]
        print("\nÚltimas transações:")
        for t in recent:
            print(f"ID {t.id}: {format_date(t.data)} - {t.descricao} - {format_currency(t.valor)}")
        
        try:
            trans_id = int(input("\nID para deletar: "))
            transaction = self.finance.get_transaction_by_id(trans_id)
            
            if not transaction:
                print("✗ Não encontrada!")
                input("\nPressione ENTER...")
                return
            
            print(f"\n⚠ Deletar: {transaction.descricao} - {format_currency(transaction.valor)}?")
            confirm = input("Confirmar (S/N)? ").strip().upper()
            
            if confirm == 'S':
                if self.finance.delete_transaction(trans_id):
                    self.storage.save(self.finance.transactions, self.finance.categories)
                    print("\n✓ Deletada!")
                else:
                    print("\n✗ Erro!")
            else:
                print("\n✗ Cancelado!")
                
        except ValueError:
            print("✗ ID inválido!")
        
        input("\nPressione ENTER...")
    
    def view_summary(self):
        """Exibe resumo financeiro"""
        self.clear_screen()
        print("=" * 60)
        print("RESUMO FINANCEIRO".center(60))
        print("=" * 60)
        
        if not self.finance.transactions:
            print("\nNenhuma transação!")
            input("\nPressione ENTER...")
            return
        
        # Escolher período
        print("\n1. Este mês")
        print("2. Últimos 30 dias")
        print("3. Últimos 3 meses")
        print("4. Este ano")
        print("5. Todo período")
        
        choice = input("\nPeríodo (1-5): ").strip()
        
        now = datetime.now()
        
        if choice == '1':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered = self.finance.filter_by_period(start, now)
            period_name = "Este Mês"
        elif choice == '2':
            start = now - timedelta(days=30)
            filtered = self.finance.filter_by_period(start, now)
            period_name = "Últimos 30 Dias"
        elif choice == '3':
            start = now - timedelta(days=90)
            filtered = self.finance.filter_by_period(start, now)
            period_name = "Últimos 3 Meses"
        elif choice == '4':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered = self.finance.filter_by_period(start, now)
            period_name = "Este Ano"
        else:
            filtered = self.finance.transactions
            period_name = "Todo Período"
        
        if not filtered:
            print(f"\n✗ Sem transações em: {period_name}")
            input("\nPressione ENTER...")
            return
        
        # Calcular resumo
        summary = self.finance.calculate_summary(filtered)
        
        self.clear_screen()
        print("=" * 60)
        print(f"RESUMO: {period_name}".center(60))
        print("=" * 60)
        
        print(f"\n{'RECEITAS:':<30} {format_currency(summary['total_receitas']):>25}")
        print(f"{'DESPESAS:':<30} {format_currency(summary['total_despesas']):>25}")
        print("-" * 60)
        print(f"{'SALDO:':<30} {format_currency(summary['saldo']):>25}")
        
        # Por categoria
        cat_totals = self.finance.calculate_by_category(filtered, 'despesa')
        
        if cat_totals:
            print("\n" + "=" * 60)
            print("DESPESAS POR CATEGORIA".center(60))
            print("=" * 60)
            
            for cat, total in cat_totals.items():
                percent = (total / summary['total_despesas'] * 100) if summary['total_despesas'] > 0 else 0
                from utils.formatters import create_progress_bar
                bar = create_progress_bar(total, summary['total_despesas'], 40)
                
                print(f"\n{cat:<20} {format_currency(total):>15} ({percent:>5.1f}%)")
                print(f"{bar}")
        
        # Estatísticas
        stats = self.finance.get_statistics(filtered)
        
        if stats:
            print("\n" + "=" * 60)
            print("ESTATÍSTICAS".center(60))
            print("=" * 60)
            
            if 'media_receitas' in stats:
                print(f"\nMédia de receitas: {format_currency(stats['media_receitas'])}")
            
            if 'media_despesas' in stats:
                print(f"Média de despesas: {format_currency(stats['media_despesas'])}")
            
            if 'maior_despesa_obj' in stats:
                obj = stats['maior_despesa_obj']
                print(f"\nMaior despesa: {obj.descricao} - {format_currency(obj.valor)}")
        
        print("\n" + "=" * 60)
        input("\nPressione ENTER...")
    
    def view_chart(self):
        """Exibe gráfico mensal"""
        self.clear_screen()
        print("=" * 60)
        print("GRÁFICO MENSAL".center(60))
        print("=" * 60)
        
        if not self.finance.transactions:
            print("\nNenhuma transação!")
            input("\nPressione ENTER...")
            return
        
        monthly_data = self.finance.get_monthly_data(12)
        
        if not monthly_data:
            print("\nDados insuficientes!")
            input("\nPressione ENTER...")
            return
        
        max_value = max(
            max(m['receitas'], m['despesas'])
            for m in monthly_data
        )
        
        print("\nLegenda: [██] Receitas  [▓▓] Despesas\n")
        
        from utils.formatters import create_progress_bar
        
        for month in monthly_data:
            receitas_bar = create_progress_bar(month['receitas'], max_value, CHART_BAR_LENGTH, '█')
            despesas_bar = create_progress_bar(month['despesas'], max_value, CHART_BAR_LENGTH, '▓')
            saldo = month['receitas'] - month['despesas']
            
            print(f"{month['name']:<10} {receitas_bar:<50} {format_currency(month['receitas']):>15}")
            print(f"{'':<10} {despesas_bar:<50} {format_currency(month['despesas']):>15}")
            print(f"{'':<10} Saldo: {format_currency(saldo)}")
            print()
        
        input("\nPressione ENTER...")
    
    def search_transactions(self):
        """Busca transações"""
        self.clear_screen()
        print("=" * 60)
        print("BUSCAR TRANSAÇÕES".center(60))
        print("=" * 60)
        
        print("\n1. Por descrição")
        print("2. Por categoria")
        print("3. Por valor (faixa)")
        print("4. Voltar")
        
        choice = input("\nOpção (1-4): ").strip()
        
        if choice == '1':
            termo = input("\nTermo de busca: ").strip()
            filtered = self.finance.filter_by_description(termo)
            
            if filtered:
                self.list_transactions(filtered)
            else:
                print("\n✗ Nenhuma transação encontrada!")
                input("\nPressione ENTER...")
        
        elif choice == '2':
            all_cats = set(t.categoria for t in self.finance.transactions)
            print("\nCategorias:")
            for i, cat in enumerate(sorted(all_cats), 1):
                print(f"{i}. {cat}")
            
            cat_nome = input("\nNome da categoria: ").strip()
            filtered = self.finance.filter_by_category(cat_nome)
            
            if filtered:
                self.list_transactions(filtered)
            else:
                print("\n✗ Nenhuma transação encontrada!")
                input("\nPressione ENTER...")
        
        elif choice == '3':
            try:
                min_str = input("\nValor mínimo: ").strip()
                max_str = input("Valor máximo: ").strip()
                
                valid_min, min_val = validate_value(min_str)
                valid_max, max_val = validate_value(max_str)
                
                if valid_min and valid_max:
                    filtered = self.finance.filter_by_value_range(min_val, max_val)
                    
                    if filtered:
                        self.list_transactions(filtered)
                    else:
                        print("\n✗ Nenhuma transação encontrada!")
                        input("\nPressione ENTER...")
                else:
                    print("\n✗ Valores inválidos!")
                    input("\nPressione ENTER...")
            except Exception:
                print("\n✗ Erro na busca!")
                input("\nPressione ENTER...")
    
    def manage_categories(self):
        """Gerenciar categorias"""
        self.clear_screen()
        print("=" * 60)
        print("GERENCIAR CATEGORIAS".center(60))
        print("=" * 60)
        
        print("\n1. Ver categorias")
        print("2. Adicionar categoria")
        print("3. Remover categoria")
        print("4. Voltar")
        
        choice = input("\nOpção (1-4): ").strip()
        
        if choice == '1':
            print("\n--- RECEITAS ---")
            for cat in self.finance.categories.get_categories('receita'):
                print(f"  • {cat}")
            
            print("\n--- DESPESAS ---")
            for cat in self.finance.categories.get_categories('despesa'):
                print(f"  • {cat}")
            
            input("\nPressione ENTER...")
        
        elif choice == '2':
            tipo = input("\nAdicionar em (1-Receita / 2-Despesa): ").strip()
            tipo_key = 'receita' if tipo == '1' else 'despesa' if tipo == '2' else None
            
            if tipo_key:
                nova_cat = input("Nome da nova categoria: ").strip()
                
                if self.finance.categories.add_category(tipo_key, nova_cat):
                    self.storage.save(self.finance.transactions, self.finance.categories)
                    print(f"\n✓ Categoria '{nova_cat}' adicionada!")
                else:
                    print("\n✗ Categoria inválida ou já existe!")
            
            input("\nPressione ENTER...")
        
        elif choice == '3':
            tipo = input("\nRemover de (1-Receita / 2-Despesa): ").strip()
            tipo_key = 'receita' if tipo == '1' else 'despesa' if tipo == '2' else None
            
            if tipo_key:
                cats = self.finance.categories.get_categories(tipo_key)
                print(f"\nCategorias de {tipo_key}:")
                for i, cat in enumerate(cats, 1):
                    print(f"{i}. {cat}")
                
                try:
                    idx = int(input("\nNúmero para remover: ")) - 1
                    cat_name = cats[idx]
                    
                    if self.finance.categories.remove_category(tipo_key, cat_name):
                        self.storage.save(self.finance.transactions, self.finance.categories)
                        print(f"\n✓ Categoria '{cat_name}' removida!")
                    else:
                        print("\n✗ Erro ao remover!")
                except (ValueError, IndexError):
                    print("\n✗ Opção inválida!")
            
            input("\nPressione ENTER...")
    
    def export_csv(self):
        """Exporta para CSV"""
        self.clear_screen()
        print("=" * 60)
        print("EXPORTAR PARA CSV".center(60))
        print("=" * 60)
        
        if not self.finance.transactions:
            print("\nNenhuma transação para exportar!")
            input("\nPressione ENTER...")
            return
        
        filename = input("\nNome do arquivo (sem extensão): ").strip()
        if not filename:
            filename = f"financas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = f"{filename}.csv"
        
        if self.storage.export_to_csv(self.finance.transactions, filename):
            print(f"\n✓ Exportado: {filename}")
            print(f"Total: {len(self.finance.transactions)} transações")
        else:
            print("\n✗ Erro ao exportar!")
        
        input("\nPressione ENTER...")
    
    def run(self):
        """Loop principal"""
        print(f"\n✓ Sistema iniciado! {len(self.finance.transactions)} transações carregadas.\n")
        input("Pressione ENTER para continuar...")
        
        while True:
            self.show_menu()
            choice = input("\nOpção (1-10): ").strip()
            
            if choice == '1':
                self.add_transaction()
            elif choice == '2':
                self.list_transactions()
            elif choice == '3':
                self.edit_transaction()
            elif choice == '4':
                self.delete_transaction()
            elif choice == '5':
                self.view_summary()
            elif choice == '6':
                self.view_chart()
            elif choice == '7':
                self.search_transactions()
            elif choice == '8':
                self.manage_categories()
            elif choice == '9':
                self.export_csv()
            elif choice == '10':
                self.clear_screen()
                print("\n" + "=" * 60)
                print("Obrigado por usar o Sistema!".center(60))
                print("Dados salvos automaticamente.".center(60))
                print("=" * 60 + "\n")
                break
            else:
                print("\n✗ Opção inválida!")
                input("\nPressione ENTER...")