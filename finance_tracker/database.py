import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join("data", "finance.db")

def create_connection():
    """Cria (ou conecta) ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    """Cria a tabela de transações, se ainda não existir."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,            -- 'receita' ou 'despesa'
            description TEXT NOT NULL,
            category TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL             -- formato: YYYY-MM-DD
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Iniciando criação do banco de dados...")
    create_table()
    print("Banco de dados criado com sucesso!")
