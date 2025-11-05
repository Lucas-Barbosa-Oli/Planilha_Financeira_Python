import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from transactions import (
    adicionar_transacao,
    listar_transacoes,
    deletar_transacao_por_id,
    limpar_todas_transacoes,
    editar_transacao
)

from database import criar_tabela, criar_conexao


# ==============================
# FUNÇÕES DE INSERÇÃO E VISUALIZAÇÃO
# ==============================
def adicionar_transacao_menu():
    tipo = input("Tipo (receita/despesa): ").lower()
    descricao = input("Descrição: ")
    categoria = input("Categoria: ")
    valor = float(input("Valor: "))
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    adicionar_transacao(tipo, descricao, categoria, valor, data)


def listar_transacoes_menu():
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")
    transacoes = cursor.fetchall()

    if not transacoes:
        print("Nenhuma transação encontrada.\n")
        return

    print("\n===== HISTÓRICO DE TRANSAÇÕES =====")
    for t in transacoes:
        print(f"[{t[0]}] {t[1].capitalize()} | {t[2]} | {t[3]} | R$ {t[4]:.2f} | {t[5]}")
    print()


# ==============================
# FUNÇÃO DE FILTROS + EXPORTAÇÃO + GRÁFICOS
# ==============================
def filtrar_transacoes_menu():
    """Permite filtrar e exportar transações com gráficos e resumo."""
    conn = criar_conexao()
    cursor = conn.cursor()

    print("\n=== FILTROS DISPONÍVEIS ===")
    print("1 - Por tipo (receita/despesa)")
    print("2 - Por mês e ano")
    print("3 - Por categoria")
    print("4 - Por intervalo de datas")
    print("0 - Voltar")
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        tipo = input("Digite o tipo (receita/despesa): ").lower()
        cursor.execute("SELECT * FROM transacoes WHERE tipo = ? ORDER BY data DESC", (tipo,))

    elif opcao == "2":
        mes = input("Digite o mês (ex: 03): ")
        ano = input("Digite o ano (ex: 2025): ")
        cursor.execute("""
            SELECT * FROM transacoes
            WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ?
            ORDER BY data DESC
        """, (mes, ano))

    elif opcao == "3":
        categoria = input("Digite a categoria: ")
        cursor.execute("SELECT * FROM transacoes WHERE categoria = ? ORDER BY data DESC", (categoria,))

    elif opcao == "4":
        data_inicio = input("Data inicial (YYYY-MM-DD): ")
        data_fim = input("Data final (YYYY-MM-DD): ")
        cursor.execute("""
            SELECT * FROM transacoes
            WHERE date(data) BETWEEN date(?) AND date(?)
            ORDER BY data ASC
        """, (data_inicio, data_fim))

    elif opcao == "0":
        conn.close()
        return

    else:
        print("❌ Opção inválida.")
        conn.close()
        return

    transacoes = cursor.fetchall()
    conn.close()

    if not transacoes:
        print("\n⚠️ Nenhuma transação encontrada com os filtros aplicados.\n")
        return

    # Exibe resultados
    print("\n=== RESULTADO DO FILTRO ===")
    total_receita = total_despesa = 0
    for t in transacoes:
        print(f"[{t[0]}] {t[1].capitalize()} | {t[2]} | {t[3]} | R$ {t[4]:.2f} | {t[5]}")
        if t[1] == "receita":
            total_receita += t[4]
        elif t[1] == "despesa":
            total_despesa += t[4]

    saldo = total_receita - total_despesa
    print("\n===== RESUMO =====")
    print(f"Total de Receitas: R$ {total_receita:.2f}")
    print(f"Total de Despesas: R$ {total_despesa:.2f}")
    print(f"Saldo Final: R$ {saldo:.2f}\n")

    # Pergunta sobre exportação
    print("Deseja exportar o resultado?")
    print("1 - CSV  |  2 - PDF  |  3 - Gráfico  |  0 - Não exportar")
    escolha = input("Escolha uma opção: ")

    if escolha == "1":
        exportar_csv(transacoes)
    elif escolha == "2":
        exportar_pdf(transacoes)
    elif escolha == "3":
        gerar_graficos(transacoes)


# ==============================
# FUNÇÕES DE EXPORTAÇÃO
# ==============================
def exportar_csv(transacoes):
    nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["ID", "Tipo", "Descrição", "Categoria", "Valor", "Data"])
        writer.writerows(transacoes)
    print(f"\n✅ Relatório exportado para {nome_arquivo}\n")


def exportar_pdf(transacoes):
    nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, altura - 50, "Relatório Financeiro")

    c.setFont("Helvetica", 10)
    y = altura - 100
    for t in transacoes:
        linha = f"[{t[0]}] {t[1].capitalize()} | {t[2]} | {t[3]} | R$ {t[4]:.2f} | {t[5]}"
        c.drawString(50, y, linha)
        y -= 15
        if y < 50:
            c.showPage()
            y = altura - 50
            c.setFont("Helvetica", 10)

    c.save()
    print(f"\n✅ Relatório exportado para {nome_arquivo}\n")


# ==============================
# FUNÇÃO DE GRÁFICOS
# ==============================
def gerar_graficos(transacoes):
    categorias = {}
    for t in transacoes:
        cat = t[3]
        valor = t[4]
        if cat not in categorias:
            categorias[cat] = 0
        categorias[cat] += valor

    plt.figure(figsize=(7, 5))
    plt.bar(categorias.keys(), categorias.values())
    plt.title("Despesas/Receitas por Categoria")
    plt.xlabel("Categoria")
    plt.ylabel("Valor (R$)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


# ==============================
# SALDO
# ==============================
def calcular_saldo():
    conexao = criar_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'receita'")
    receitas = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'despesa'")
    despesas = cursor.fetchone()[0] or 0

    saldo = receitas - despesas
    print(f"\n💰 Saldo atual: R$ {saldo:.2f}\n")
    conexao.close()


# ==============================
# MENU PRINCIPAL
# ==============================
def menu():
    criar_tabela()

    while True:
        print("""
===== MENU FINANCEIRO =====
1 - Adicionar transação
2 - Listar transações
3 - Ver saldo
4 - Excluir transação por ID
5 - Limpar todas as transações
6 - Filtrar/Exportar/Gráficos
0 - Sair
============================
        """)
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_transacao_menu()
        elif opcao == "2":
            listar_transacoes_menu()
        elif opcao == "3":
            calcular_saldo()
        elif opcao == "4":
            id_transacao = input("Digite o ID da transação que deseja excluir: ")
            deletar_transacao_por_id(id_transacao)
        elif opcao == "5":
            confirmacao = input("Tem certeza que deseja limpar todas as transações? (s/n): ").lower()
            if confirmacao == "s":
                limpar_todas_transacoes()
        elif opcao == "6":
            filtrar_transacoes_menu()
        elif opcao == "0":
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida!\n")


if __name__ == "__main__":
    menu()
