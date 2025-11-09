# main.py
from datetime import datetime
from utils import clear_screen, format_money, ensure_dirs, EXPORTS_DIR
from tracker import FinanceTracker
import os

def pause():
    input("\nPressione ENTER para continuar...")

def print_transactions_list(transactions):
    if not transactions:
        print("Nenhuma transação encontrada.")
        return
    print(f"{'ID':<5} {'Data':<12} {'Tipo':<8} {'Categoria':<15} {'Descrição':<30} {'Valor':>12}")
    print("-" * 90)
    for t in transactions:
        data_fmt = datetime.fromisoformat(t['data']).strftime('%d/%m/%Y')
        valor_fmt = format_money(t['valor'])
        print(f"{t['id']:<5} {data_fmt:<12} {t['tipo']:<8} {t['categoria'][:15]:<15} {t['descricao'][:30]:<30} {valor_fmt:>12}")

def main():
    ensure_dirs()
    tracker = FinanceTracker()
    while True:
        clear_screen()
        print("SISTEMA DE CONTROLE FINANCEIRO")
        print("=============================")
        print("1 - Adicionar transação")
        print("2 - Listar transações")
        print("3 - Editar transação")
        print("4 - Deletar transação")
        print("5 - Resumo / Análises")
        print("6 - Exportar (CSV / PDF)")
        print("7 - Limpar todas as transações")
        print("0 - Sair")
        choice = input("\nEscolha uma opção: ").strip()
        if choice == '1':
            clear_screen()
            tipo = input("Tipo (receita/despesa): ").strip().lower()
            descricao = input("Descrição: ").strip()
            categoria = input("Categoria: ").strip()
            try:
                valor = float(input("Valor (use '.' como separador): ").strip().replace(',', '.'))
            except ValueError:
                print("Valor inválido.")
                pause()
                continue
            data_input = input("Data (DD/MM/AAAA) ou ENTER para hoje: ").strip()
            if data_input:
                try:
                    data_iso = datetime.strptime(data_input, '%d/%m/%Y').isoformat()
                except ValueError:
                    print("Data inválida.")
                    pause()
                    continue
            else:
                data_iso = datetime.now().isoformat()
            tx = tracker.add_transaction(tipo, descricao, categoria, valor, data_iso)
            print(f"Transação adicionada (ID {tx['id']}).")
            pause()

        elif choice == '2':
            clear_screen()
            txs = tracker.list_transactions()
            print_transactions_list(txs)
            pause()

        elif choice == '3':
            clear_screen()
            txs = tracker.list_transactions()
            print_transactions_list(txs[:20])  # mostrar primeiros 20 para referência
            try:
                tx_id = int(input("\nID para editar: ").strip())
            except ValueError:
                print("ID inválido.")
                pause()
                continue
            tx = tracker.get_transaction(tx_id)
            if not tx:
                print("Transação não encontrada.")
                pause()
                continue
            print("Deixe em branco para manter o valor atual.")
            new_desc = input(f"Descrição [{tx['descricao']}]: ").strip() or tx['descricao']
            new_cat = input(f"Categoria [{tx['categoria']}]: ").strip() or tx['categoria']
            new_val = input(f"Valor [{tx['valor']}]: ").strip()
            if new_val:
                try:
                    new_val_f = float(new_val.replace(',', '.'))
                except ValueError:
                    print("Valor inválido.")
                    pause()
                    continue
            else:
                new_val_f = tx['valor']
            new_date = input(f"Data (DD/MM/AAAA) [{datetime.fromisoformat(tx['data']).strftime('%d/%m/%Y')}]: ").strip()
            if new_date:
                try:
                    new_date_iso = datetime.strptime(new_date, '%d/%m/%Y').isoformat()
                except ValueError:
                    print("Data inválida.")
                    pause()
                    continue
            else:
                new_date_iso = tx['data']
            ok = tracker.edit_transaction(tx_id, descricao=new_desc, categoria=new_cat, valor=new_val_f, data=new_date_iso)
            print("Atualizado." if ok else "Falha ao atualizar.")
            pause()

        elif choice == '4':
            clear_screen()
            txs = tracker.list_transactions()
            print_transactions_list(txs[:20])
            try:
                tx_id = int(input("\nID para deletar: ").strip())
            except ValueError:
                print("ID inválido.")
                pause()
                continue
            confirm = input("Confirmar exclusão (s/N)? ").strip().lower()
            if confirm == 's':
                ok = tracker.delete_transaction(tx_id)
                print("Deletado." if ok else "Não encontrado.")
            else:
                print("Cancelado.")
            pause()

        elif choice == '5':
            clear_screen()
            receitas, despesas, saldo = tracker.compute_balance()
            print(f"Receitas: {format_money(receitas)}")
            print(f"Despesas: {format_money(despesas)}")
            print(f"Saldo: {format_money(saldo)}\n")
            # monthly accumulated
            m = tracker.monthly_summary()
            if m:
                print("\nHistórico acumulado mensal (últimos 12 meses):")
                keys = list(m.keys())[-12:]
                for k in keys:
                    v = m[k]
                    print(f"{k}: Receitas {format_money(v['receitas'])}  Despesas {format_money(v['despesas'])}  Saldo {format_money(v['saldo'])}")
            # top 5 categories
            top5 = tracker.top5_categories()
            if top5:
                print("\nTop 5 categorias (despesas):")
                for i, (cat, total) in enumerate(top5, 1):
                    print(f"{i}. {cat} - {format_money(total)}")
            # moving average expenses
            months, values, ma = tracker.moving_average_expenses(window=3)
            if months:
                print("\nMédia móvel de despesas (janela=3):")
                for m_name, val, mval in zip(months, values, ma):
                    print(f"{m_name}: {format_money(val)} | MA: {format_money(mval)}")
            pause()

        elif choice == '6':
            clear_screen()
            print("Exportar")
            print("1 - CSV")
            print("2 - PDF")
            opt = input("Escolha: ").strip()
            filename = input("Nome do arquivo (sem extensão) ou ENTER para default: ").strip()
            if not filename:
                filename = f"relatorios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = os.path.join("exports", filename + (".csv" if opt == '1' else ".pdf"))
            try:
                if opt == '1':
                    tracker.export_csv(filepath)
                    print(f"Exportado CSV: {filepath}")
                elif opt == '2':
                    tracker.export_pdf(filepath)
                    print(f"Exportado PDF: {filepath}")
                else:
                    print("Opção inválida.")
            except Exception as e:
                print(f"Erro na exportação: {e}")
            pause()

        elif choice == '7':
            confirm = input("Limpar todas as transações? Isso é irreversível (s/N): ").strip().lower()
            if confirm == 's':
                tracker.clear_transactions()
                print("Todas as transações removidas.")
            else:
                print("Cancelado.")
            pause()

        elif choice == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")
            pause()

if __name__ == "__main__":
    main()
