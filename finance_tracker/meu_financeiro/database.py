import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join("data", "finance.db")

def criar_conexao():
    """Cria (ou conecta) ao banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def criar_tabela():
    """Cria a tabela de transações, se ainda não existir."""
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,             -- 'receita' ou 'despesa'
            descricao TEXT NOT NULL,
            categoria TEXT,
            valor REAL NOT NULL,
            data TEXT NOT NULL              -- formato: YYYY-MM-DD
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Iniciando criação do banco de dados...")
    criar_tabela()
    print("Banco de dados criado com sucesso!")
