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
