import sqlite3
from database import create_connection

# -------------------------------------------------
# Função para adicionar uma nova transação
# -------------------------------------------------
def add_transaction(type, description, category, amount, date):
    """Adiciona uma nova transação ao banco de dados."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (type, description, category, amount, date)
        VALUES (?, ?, ?, ?, ?)
    """, (type, description, category, amount, date))

    conn.commit()
    conn.close()
    print("✅ Transação adicionada com sucesso!")


# -------------------------------------------------
# Função para listar todas as transações
# -------------------------------------------------
def list_transactions():
    """Retorna e exibe todas as transações salvas."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY date ASC")
    rows = cursor.fetchall()

    if len(rows) == 0:
        print("⚠️ Nenhuma transação encontrada.")
    else:
        print("\n=== LISTA DE TRANSAÇÕES ===")
        for row in rows:
            print(f"ID: {row[0]} | Tipo: {row[1]} | Descrição: {row[2]} | Categoria: {row[3]} | Valor: R${row[4]:.2f} | Data: {row[5]}")

    conn.close()

# --- EXCLUIR UMA TRANSAÇÃO POR ID ---
def deletar_transacao_por_id(id):
    """Exclui uma transação específica pelo ID."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Transação com ID {id} excluída com sucesso.")
    else:
        print(f"⚠️ Nenhuma transação encontrada com o ID {id}.")

    conn.close()


# --- LIMPAR TODAS AS TRANSAÇÕES ---
def limpar_todas_transacoes():
    """Remove todas as transações do banco."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transactions')
    conn.commit()
    conn.close()

    print("🗑️ Todas as transações foram removidas com sucesso.")

