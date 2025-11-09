#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Controle Financeiro Pessoal
Gerenciamento completo de transações financeiras via terminal
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

class FinanceTracker:
    def __init__(self, filename='financas.json'):
        self.filename = filename
        self.transactions = []
        self.categories = {
            'receita': ['Salário', 'Freelance', 'Investimentos', 'Outros Ganhos'],
            'despesa': ['Alimentação', 'Transporte', 'Moradia', 'Saúde', 
                       'Educação', 'Lazer', 'Contas', 'Compras', 'Outros Gastos']
        }
        self.load_data()
    
    def load_data(self):
        """Carrega dados do arquivo JSON"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', [])
                    custom_categories = data.get('categories', {})
                    if custom_categories:
                        self.categories.update(custom_categories)
                print(f"✓ Dados carregados: {len(self.transactions)} transações")
            except Exception as e:
                print(f"⚠ Erro ao carregar dados: {e}")
                self.transactions = []
        else:
            print("⚠ Nenhum arquivo de dados encontrado. Iniciando novo sistema.")
    
    def save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            data = {
                'transactions': self.transactions,
                'categories': self.categories,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✓ Dados salvos com sucesso!")
        except Exception as e:
            print(f"✗ Erro ao salvar dados: {e}")
    
    def add_transaction(self):
        """Adiciona nova transação"""
        clear_screen()
        print("=" * 60)
        print("ADICIONAR NOVA TRANSAÇÃO".center(60))
        print("=" * 60)
        
        # Tipo de transação
        print("\n1. Receita")
        print("2. Despesa")
        tipo_choice = input("\nEscolha o tipo (1-2): ").strip()
        
        if tipo_choice == '1':
            tipo = 'receita'
        elif tipo_choice == '2':
            tipo = 'despesa'
        else:
            print("✗ Opção inválida!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Categoria
        print(f"\n--- Categorias de {tipo.upper()} ---")
        for i, cat in enumerate(self.categories[tipo], 1):
            print(f"{i}. {cat}")
        
        cat_choice = input(f"\nEscolha a categoria (1-{len(self.categories[tipo])}): ").strip()
        try:
            categoria = self.categories[tipo][int(cat_choice) - 1]
        except (ValueError, IndexError):
            print("✗ Categoria inválida!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Descrição
        descricao = input("\nDescrição: ").strip()
        if not descricao:
            print("✗ Descrição não pode ser vazia!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Valor
        try:
            valor_str = input("Valor (R$): ").strip().replace(',', '.')
            valor = float(valor_str)
            if valor <= 0:
                print("✗ Valor deve ser maior que zero!")
                input("\nPressione ENTER para continuar...")
                return
        except ValueError:
            print("✗ Valor inválido!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Data
        data_input = input("Data (DD/MM/AAAA) ou ENTER para hoje: ").strip()
        if data_input:
            try:
                data = datetime.strptime(data_input, '%d/%m/%Y').isoformat()
            except ValueError:
                print("✗ Data inválida! Use DD/MM/AAAA")
                input("\nPressione ENTER para continuar...")
                return
        else:
            data = datetime.now().isoformat()
        
        # Criar transação
        transaction = {
            'id': len(self.transactions) + 1,
            'tipo': tipo,
            'categoria': categoria,
            'descricao': descricao,
            'valor': valor,
            'data': data,
            'criado_em': datetime.now().isoformat()
        }
        
        self.transactions.append(transaction)
        self.save_data()
        
        print(f"\n✓ {tipo.capitalize()} de R$ {valor:.2f} adicionada com sucesso!")
        input("\nPressione ENTER para continuar...")
    
    def list_transactions(self, filtered_transactions=None):
        """Lista todas as transações"""
        clear_screen()
        transactions_to_show = filtered_transactions if filtered_transactions is not None else self.transactions
        
        if not transactions_to_show:
            print("=" * 60)
            print("NENHUMA TRANSAÇÃO ENCONTRADA".center(60))
            print("=" * 60)
            input("\nPressione ENTER para continuar...")
            return
        
        print("=" * 100)
        print("LISTA DE TRANSAÇÕES".center(100))
        print("=" * 100)
        
        # Cabeçalho
        print(f"\n{'ID':<5} {'Data':<12} {'Tipo':<10} {'Categoria':<15} {'Descrição':<25} {'Valor':>15}")
        print("-" * 100)
        
        # Ordenar por data (mais recente primeiro)
        sorted_trans = sorted(transactions_to_show, key=lambda x: x['data'], reverse=True)
        
        for t in sorted_trans:
            data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
            tipo_symbol = '+' if t['tipo'] == 'receita' else '-'
            valor_fmt = f"R$ {tipo_symbol}{t['valor']:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
            
            print(f"{t['id']:<5} {data_fmt:<12} {t['tipo']:<10} {t['categoria']:<15} "
                  f"{t['descricao'][:25]:<25} {valor_fmt:>15}")
        
        print("-" * 100)
        print(f"Total de transações: {len(transactions_to_show)}")
        input("\nPressione ENTER para continuar...")
    
    def edit_transaction(self):
        """Edita uma transação existente"""
        clear_screen()
        if not self.transactions:
            print("Nenhuma transação para editar!")
            input("\nPressione ENTER para continuar...")
            return
        
        print("=" * 60)
        print("EDITAR TRANSAÇÃO".center(60))
        print("=" * 60)
        
        # Mostrar últimas 10 transações
        print("\nÚltimas transações:")
        recent = sorted(self.transactions, key=lambda x: x['data'], reverse=True)[:10]
        for t in recent:
            data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
            print(f"ID {t['id']}: {data_fmt} - {t['descricao']} - R$ {t['valor']:.2f}")
        
        try:
            trans_id = int(input("\nDigite o ID da transação para editar: "))
            transaction = next((t for t in self.transactions if t['id'] == trans_id), None)
            
            if not transaction:
                print("✗ Transação não encontrada!")
                input("\nPressione ENTER para continuar...")
                return
            
            print(f"\n--- Editando: {transaction['descricao']} ---")
            print("(Pressione ENTER para manter o valor atual)")
            
            # Nova descrição
            new_desc = input(f"Descrição [{transaction['descricao']}]: ").strip()
            if new_desc:
                transaction['descricao'] = new_desc
            
            # Novo valor
            new_valor = input(f"Valor [{transaction['valor']:.2f}]: ").strip()
            if new_valor:
                transaction['valor'] = float(new_valor.replace(',', '.'))
            
            # Nova data
            data_atual = datetime.fromisoformat(transaction['data']).strftime('%d/%m/%Y')
            new_data = input(f"Data [{data_atual}]: ").strip()
            if new_data:
                transaction['data'] = datetime.strptime(new_data, '%d/%m/%Y').isoformat()
            
            self.save_data()
            print("\n✓ Transação atualizada com sucesso!")
            
        except ValueError:
            print("✗ Entrada inválida!")
        except Exception as e:
            print(f"✗ Erro: {e}")
        
        input("\nPressione ENTER para continuar...")
    
    def delete_transaction(self):
        """Deleta uma transação"""
        clear_screen()
        if not self.transactions:
            print("Nenhuma transação para deletar!")
            input("\nPressione ENTER para continuar...")
            return
        
        print("=" * 60)
        print("DELETAR TRANSAÇÃO".center(60))
        print("=" * 60)
        
        # Mostrar últimas 10 transações
        print("\nÚltimas transações:")
        recent = sorted(self.transactions, key=lambda x: x['data'], reverse=True)[:10]
        for t in recent:
            data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
            print(f"ID {t['id']}: {data_fmt} - {t['descricao']} - R$ {t['valor']:.2f}")
        
        try:
            trans_id = int(input("\nDigite o ID da transação para deletar: "))
            transaction = next((t for t in self.transactions if t['id'] == trans_id), None)
            
            if not transaction:
                print("✗ Transação não encontrada!")
                input("\nPressione ENTER para continuar...")
                return
            
            # Confirmação
            print(f"\n⚠ Deletar: {transaction['descricao']} - R$ {transaction['valor']:.2f}?")
            confirm = input("Confirmar (S/N)? ").strip().upper()
            
            if confirm == 'S':
                self.transactions.remove(transaction)
                self.save_data()
                print("\n✓ Transação deletada com sucesso!")
            else:
                print("\n✗ Operação cancelada!")
                
        except ValueError:
            print("✗ ID inválido!")
        except Exception as e:
            print(f"✗ Erro: {e}")
        
        input("\nPressione ENTER para continuar...")
    
    def view_summary(self):
        """Visualiza resumo financeiro"""
        clear_screen()
        print("=" * 60)
        print("RESUMO FINANCEIRO".center(60))
        print("=" * 60)
        
        if not self.transactions:
            print("\nNenhuma transação registrada!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Período
        print("\n1. Este mês")
        print("2. Últimos 30 dias")
        print("3. Últimos 3 meses")
        print("4. Este ano")
        print("5. Todo o período")
        print("6. Período personalizado")
        
        choice = input("\nEscolha o período (1-6): ").strip()
        
        now = datetime.now()
        filtered = self.transactions
        
        if choice == '1':  # Este mês
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered = [t for t in self.transactions if datetime.fromisoformat(t['data']) >= start]
            period_name = "Este Mês"
        elif choice == '2':  # Últimos 30 dias
            start = now - timedelta(days=30)
            filtered = [t for t in self.transactions if datetime.fromisoformat(t['data']) >= start]
            period_name = "Últimos 30 Dias"
        elif choice == '3':  # Últimos 3 meses
            start = now - timedelta(days=90)
            filtered = [t for t in self.transactions if datetime.fromisoformat(t['data']) >= start]
            period_name = "Últimos 3 Meses"
        elif choice == '4':  # Este ano
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered = [t for t in self.transactions if datetime.fromisoformat(t['data']) >= start]
            period_name = "Este Ano"
        elif choice == '5':  # Todo período
            period_name = "Todo o Período"
        elif choice == '6':  # Personalizado
            try:
                start_str = input("Data inicial (DD/MM/AAAA): ").strip()
                end_str = input("Data final (DD/MM/AAAA): ").strip()
                start = datetime.strptime(start_str, '%d/%m/%Y')
                end = datetime.strptime(end_str, '%d/%m/%Y').replace(hour=23, minute=59, second=59)
                filtered = [t for t in self.transactions 
                           if start <= datetime.fromisoformat(t['data']) <= end]
                period_name = f"{start_str} até {end_str}"
            except ValueError:
                print("✗ Data inválida!")
                input("\nPressione ENTER para continuar...")
                return
        else:
            print("✗ Opção inválida!")
            input("\nPressione ENTER para continuar...")
            return
        
        if not filtered:
            print(f"\n✗ Nenhuma transação no período: {period_name}")
            input("\nPressione ENTER para continuar...")
            return
        
        # Calcular totais
        receitas = [t for t in filtered if t['tipo'] == 'receita']
        despesas = [t for t in filtered if t['tipo'] == 'despesa']
        
        total_receitas = sum(t['valor'] for t in receitas)
        total_despesas = sum(t['valor'] for t in despesas)
        saldo = total_receitas - total_despesas
        
        clear_screen()
        print("=" * 60)
        print(f"RESUMO: {period_name}".center(60))
        print("=" * 60)
        
        print(f"\n{'RECEITAS:':<30} R$ {total_receitas:>15,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
        print(f"{'DESPESAS:':<30} R$ {total_despesas:>15,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
        print("-" * 60)
        saldo_fmt = f"R$ {saldo:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        print(f"{'SALDO:':<30} {saldo_fmt:>15}")
        
        # Resumo por categoria
        if despesas:
            print("\n" + "=" * 60)
            print("DESPESAS POR CATEGORIA".center(60))
            print("=" * 60)
            
            cat_totals = {}
            for t in despesas:
                cat = t['categoria']
                cat_totals[cat] = cat_totals.get(cat, 0) + t['valor']
            
            for cat, total in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
                percent = (total / total_despesas * 100) if total_despesas > 0 else 0
                bar_length = int(percent / 2)
                bar = '█' * bar_length
                print(f"\n{cat:<20} R$ {total:>10,.2f} ({percent:>5.1f}%)".replace(',', '_').replace('.', ',').replace('_', '.'))
                print(f"{bar}")
        
        # Estatísticas
        if len(filtered) > 1:
            print("\n" + "=" * 60)
            print("ESTATÍSTICAS".center(60))
            print("=" * 60)
            
            if receitas:
                media_receitas = statistics.mean([t['valor'] for t in receitas])
                print(f"\nMédia de receitas: R$ {media_receitas:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
            
            if despesas:
                media_despesas = statistics.mean([t['valor'] for t in despesas])
                print(f"Média de despesas: R$ {media_despesas:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
                
                maior_despesa = max(despesas, key=lambda x: x['valor'])
                print(f"\nMaior despesa: {maior_despesa['descricao']} - R$ {maior_despesa['valor']:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
        
        print("\n" + "=" * 60)
        input("\nPressione ENTER para continuar...")
    
    def export_to_csv(self):
        """Exporta transações para CSV"""
        clear_screen()
        print("=" * 60)
        print("EXPORTAR PARA CSV".center(60))
        print("=" * 60)
        
        if not self.transactions:
            print("\nNenhuma transação para exportar!")
            input("\nPressione ENTER para continuar...")
            return
        
        filename = input("\nNome do arquivo (sem extensão): ").strip()
        if not filename:
            filename = f"financas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filename = f"{filename}.csv"
        
        try:
            with open(filename, 'w', encoding='utf-8-sig') as f:
                # Cabeçalho
                f.write("ID;Data;Tipo;Categoria;Descrição;Valor\n")
                
                # Dados
                for t in sorted(self.transactions, key=lambda x: x['data']):
                    data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
                    valor_fmt = f"{t['valor']:.2f}".replace('.', ',')
                    f.write(f"{t['id']};{data_fmt};{t['tipo']};{t['categoria']};"
                           f"{t['descricao']};{valor_fmt}\n")
            
            print(f"\n✓ Arquivo exportado com sucesso: {filename}")
            print(f"Total de {len(self.transactions)} transações exportadas")
            
        except Exception as e:
            print(f"\n✗ Erro ao exportar: {e}")
        
        input("\nPressione ENTER para continuar...")
    
    def view_chart(self):
        """Visualiza gráfico em ASCII"""
        clear_screen()
        print("=" * 60)
        print("GRÁFICO MENSAL".center(60))
        print("=" * 60)
        
        if not self.transactions:
            print("\nNenhuma transação para exibir!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Agrupar por mês
        monthly_data = {}
        for t in self.transactions:
            date = datetime.fromisoformat(t['data'])
            month_key = date.strftime('%Y-%m')
            month_name = date.strftime('%b/%Y')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'name': month_name,
                    'receitas': 0,
                    'despesas': 0
                }
            
            if t['tipo'] == 'receita':
                monthly_data[month_key]['receitas'] += t['valor']
            else:
                monthly_data[month_key]['despesas'] += t['valor']
        
        # Ordenar por data
        sorted_months = sorted(monthly_data.items())[-12:]  # Últimos 12 meses
        
        if not sorted_months:
            print("\nDados insuficientes para gráfico!")
            input("\nPressione ENTER para continuar...")
            return
        
        # Encontrar valor máximo para escala
        max_value = max(
            max(data['receitas'], data['despesas']) 
            for _, data in sorted_months
        )
        
        scale = max_value / 50 if max_value > 0 else 1
        
        print("\nLegenda: [██] Receitas  [▓▓] Despesas\n")
        
        for month_key, data in sorted_months:
            receitas_bar = int(data['receitas'] / scale)
            despesas_bar = int(data['despesas'] / scale)
            saldo = data['receitas'] - data['despesas']
            
            print(f"{data['name']:<10}", end=" ")
            print(f"{'█' * receitas_bar:<50}", end=" ")
            print(f"R$ {data['receitas']:>10,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
            
            print(f"{'':<10}", end=" ")
            print(f"{'▓' * despesas_bar:<50}", end=" ")
            print(f"R$ {data['despesas']:>10,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
            
            saldo_symbol = '+' if saldo >= 0 else ''
            print(f"{'':<10} Saldo: R$ {saldo_symbol}{saldo:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'))
            print()
        
        input("\nPressione ENTER para continuar...")
    
    def manage_categories(self):
        """Gerenciar categorias"""
        clear_screen()
        print("=" * 60)
        print("GERENCIAR CATEGORIAS".center(60))
        print("=" * 60)
        
        print("\n1. Ver categorias")
        print("2. Adicionar categoria")
        print("3. Remover categoria")
        print("4. Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            print("\n--- RECEITAS ---")
            for cat in self.categories['receita']:
                print(f"  • {cat}")
            print("\n--- DESPESAS ---")
            for cat in self.categories['despesa']:
                print(f"  • {cat}")
            input("\nPressione ENTER para continuar...")
            
        elif choice == '2':
            tipo = input("\nAdicionar em (1-Receita / 2-Despesa): ").strip()
            tipo_key = 'receita' if tipo == '1' else 'despesa' if tipo == '2' else None
            
            if tipo_key:
                nova_cat = input("Nome da nova categoria: ").strip()
                if nova_cat and nova_cat not in self.categories[tipo_key]:
                    self.categories[tipo_key].append(nova_cat)
                    self.save_data()
                    print(f"✓ Categoria '{nova_cat}' adicionada!")
                else:
                    print("✗ Categoria inválida ou já existe!")
            input("\nPressione ENTER para continuar...")
            
        elif choice == '3':
            tipo = input("\nRemover de (1-Receita / 2-Despesa): ").strip()
            tipo_key = 'receita' if tipo == '1' else 'despesa' if tipo == '2' else None
            
            if tipo_key:
                print(f"\nCategorias de {tipo_key}:")
                for i, cat in enumerate(self.categories[tipo_key], 1):
                    print(f"{i}. {cat}")
                
                try:
                    idx = int(input("\nNúmero da categoria para remover: ")) - 1
                    removed = self.categories[tipo_key].pop(idx)
                    self.save_data()
                    print(f"✓ Categoria '{removed}' removida!")
                except:
                    print("✗ Opção inválida!")
            input("\nPressione ENTER para continuar...")
    
    def search_transactions(self):
        """Buscar transações"""
        clear_screen()
        print("=" * 60)
        print("BUSCAR TRANSAÇÕES".center(60))
        print("=" * 60)
        
        print("\n1. Buscar por descrição")
        print("2. Buscar por categoria")
        print("3. Buscar por valor (faixa)")
        print("4. Voltar")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            termo = input("\nDigite o termo de busca: ").strip().lower()
            filtered = [t for t in self.transactions 
                       if termo in t['descricao'].lower()]
            if filtered:
                self.list_transactions(filtered)
            else:
                print("\n✗ Nenhuma transação encontrada!")
                input("\nPressione ENTER para continuar...")
                
        elif choice == '2':
            print("\nCategorias disponíveis:")
            all_cats = set(t['categoria'] for t in self.transactions)
            for i, cat in enumerate(sorted(all_cats), 1):
                print(f"{i}. {cat}")
            
            cat_busca = input("\nDigite o nome da categoria: ").strip()
            filtered = [t for t in self.transactions if t['categoria'] == cat_busca]
            
            if filtered:
                self.list_transactions(filtered)
            else:
                print("\n✗ Nenhuma transação encontrada!")
                input("\nPressione ENTER para continuar...")
                
        elif choice == '3':
            try:
                min_val = float(input("\nValor mínimo: ").strip().replace(',', '.'))
                max_val = float(input("Valor máximo: ").strip().replace(',', '.'))
                filtered = [t for t in self.transactions 
                           if min_val <= t['valor'] <= max_val]
                
                if filtered:
                    self.list_transactions(filtered)
                else:
                    print("\n✗ Nenhuma transação encontrada!")
                    input("\nPressione ENTER para continuar...")
            except ValueError:
                print("\n✗ Valores inválidos!")
                input("\nPressione ENTER para continuar...")


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    """Exibe o menu principal"""
    clear_screen()
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


def main():
    """Função principal"""
    tracker = FinanceTracker()
    
    while True:
        show_menu()
        choice = input("\nEscolha uma opção (1-10): ").strip()
        
        if choice == '1':
            tracker.add_transaction()
        elif choice == '2':
            tracker.list_transactions()
        elif choice == '3':
            tracker.edit_transaction()
        elif choice == '4':
            tracker.delete_transaction()
        elif choice == '5':
            tracker.view_summary()
        elif choice == '6':
            tracker.view_chart()
        elif choice == '7':
            tracker.search_transactions()
        elif choice == '8':
            tracker.manage_categories()
        elif choice == '9':
            tracker.export_to_csv()
        elif choice == '10':
            clear_screen()
            print("\n" + "=" * 60)
            print("Obrigado por usar o Sistema de Controle Financeiro!".center(60))
            print("Seus dados foram salvos automaticamente.".center(60))
            print("=" * 60 + "\n")
            break
        else:
            print("\n✗ Opção inválida! Tente novamente.")
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()