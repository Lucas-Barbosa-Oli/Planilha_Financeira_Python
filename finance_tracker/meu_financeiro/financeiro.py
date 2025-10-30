import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from transactions import (
    add_transaction,
    list_transactions,
    deletar_transacao_por_id,
    limpar_todas_transacoes
)


# ==============================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==============================
def conectar_banco():
    conexao = sqlite3.connect("data/finance.db")
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            categoria TEXT,
            descricao TEXT,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
    ''')
    conexao.commit()
    return conexao

# ==============================
# FUNÇÕES DE INSERÇÃO E VISUALIZAÇÃO
# ==============================
def adicionar_transacao(conexao, tipo):
    categoria = input("Categoria: ")
    descricao = input("Descrição: ")
    valor = float(input("Valor: "))
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO transacoes (tipo, categoria, descricao, valor, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (tipo, categoria, descricao, valor, data))
    conexao.commit()
    print(f"{tipo.capitalize()} adicionada com sucesso!\n")

def listar_transacoes(conexao):
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

def calcular_saldo(conexao):
    cursor = conexao.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'receita'")
    receitas = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'despesa'")
    despesas = cursor.fetchone()[0] or 0

    saldo = receitas - despesas
    print(f"\n💰 Saldo atual: R$ {saldo:.2f}\n")

# ==============================
# FUNÇÕES DE FILTRO E ANÁLISE
# ==============================
def obter_transacoes_filtradas(conexao, filtro=None):
    cursor = conexao.cursor()

    if filtro == "tipo":
        tipo = input("Digite o tipo (receita/despesa): ").lower()
        cursor.execute("SELECT * FROM transacoes WHERE tipo = ? ORDER BY data DESC", (tipo,))
    elif filtro == "mes":
        mes = input("Digite o mês (ex: 03): ")
        ano = input("Digite o ano (ex: 2025): ")
        cursor.execute("""
            SELECT * FROM transacoes
            WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ?
            ORDER BY data DESC
        """, (mes, ano))
    elif filtro == "categoria":
        categoria = input("Digite a categoria: ")
        cursor.execute("SELECT * FROM transacoes WHERE categoria = ? ORDER BY data DESC", (categoria,))
    else:
        cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")

    return cursor.fetchall()

def mostrar_resumo(transacoes):
    total_receitas = sum(t[4] for t in transacoes if t[1] == "receita")
    total_despesas = sum(t[4] for t in transacoes if t[1] == "despesa")
    saldo = total_receitas - total_despesas

    print("\n===== RESUMO =====")
    print(f"Total de Receitas: R$ {total_receitas:.2f}")
    print(f"Total de Despesas: R$ {total_despesas:.2f}")
    print(f"Saldo Final: R$ {saldo:.2f}\n")

# ==============================
# FUNÇÕES DE EXPORTAÇÃO
# ==============================
def exportar_csv(transacoes):
    nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["ID", "Tipo", "Categoria", "Descrição", "Valor", "Data"])
        writer.writerows(transacoes)
    print(f"Relatório exportado para {nome_arquivo}\n")

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
    print(f"Relatório exportado para {nome_arquivo}\n")

# ==============================
# FUNÇÕES DE GRÁFICOS
# ==============================
def gerar_graficos(conexao):
    cursor = conexao.cursor()
    cursor.execute("SELECT categoria, SUM(valor) FROM transacoes WHERE tipo = 'despesa' GROUP BY categoria")
    dados = cursor.fetchall()

    if not dados:
        print("Nenhuma despesa para exibir gráfico.\n")
        return

    categorias = [d[0] for d in dados]
    valores = [d[1] for d in dados]

    plt.figure(figsize=(7,5))
    plt.bar(categorias, valores)
    plt.title("Despesas por Categoria")
    plt.xlabel("Categoria")
    plt.ylabel("Valor (R$)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

# ==============================
# MENU PRINCIPAL
# ==============================
def menu():
    conexao = conectar_banco()

    while True:
        print("===== MENU FINANCEIRO =====")
        print("1 - Adicionar Receita")
        print("2 - Adicionar Despesa")
        print("3 - Listar Transações")
        print("4 - Ver Saldo")
        print("5 - Filtrar Transações")
        print("6 - Exportar Relatório (CSV/PDF)")
        print("7 - Gerar Gráfico de Despesas")
        print("8 - Excluir Transação por ID")
        print("9 - Limpar Todas as Transações")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_transacao(conexao, "receita")
        elif opcao == "2":
            adicionar_transacao(conexao, "despesa")
        elif opcao == "3":
            listar_transacoes(conexao)
        elif opcao == "4":
            calcular_saldo(conexao)
        elif opcao == "5":
            filtro = input("Filtrar por (tipo/mes/categoria ou enter para todos): ").lower()
            transacoes = obter_transacoes_filtradas(conexao, filtro)
            for t in transacoes:
                print(f"[{t[0]}] {t[1].capitalize()} | {t[2]} | {t[3]} | R$ {t[4]:.2f} | {t[5]}")
            mostrar_resumo(transacoes)
        elif opcao == "6":
            transacoes = obter_transacoes_filtradas(conexao)
            print("1 - Exportar para CSV\n2 - Exportar para PDF")
            escolha = input("Escolha o formato: ")
            if escolha == "1":
                exportar_csv(transacoes)
            elif escolha == "2":
                exportar_pdf(transacoes)
        elif opcao == "7":
            gerar_graficos(conexao)
        elif opcao == "8":
            deletar_transacao_por_id(conexao)
        elif opcao == "9":
            limpar_todas_transacoes(conexao)
        elif opcao == "0":
            print("Saindo... Até logo!")
            conexao.close()
            break
        else:
            print("Opção inválida!\n")

if _name_ == "_main_":
    menu()
