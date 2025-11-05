from database import criar_conexao

# -------------------------------------------------
# Adicionar uma nova transação
# -------------------------------------------------
def adicionar_transacao(tipo, descricao, categoria, valor, data):
    """Adiciona uma nova transação ao banco de dados."""
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transacoes (tipo, descricao, categoria, valor, data)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, descricao, categoria, valor, data))

    conn.commit()
    conn.close()
    print("✅ Transação adicionada com sucesso!")


# -------------------------------------------------
# Listar todas as transações
# -------------------------------------------------
def listar_transacoes():
    """Retorna e exibe todas as transações salvas."""
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transacoes ORDER BY data ASC")
    linhas = cursor.fetchall()

    if len(linhas) == 0:
        print("⚠️ Nenhuma transação encontrada.")
    else:
        print("\n=== LISTA DE TRANSAÇÕES ===")
        for row in linhas:
            print(f"ID: {row[0]} | Tipo: {row[1]} | Descrição: {row[2]} | Categoria: {row[3]} | Valor: R${row[4]:.2f} | Data: {row[5]}")

    conn.close()


# -------------------------------------------------
# Excluir uma transação por ID
# -------------------------------------------------
def deletar_transacao_por_id(id_transacao):
    """Exclui uma transação específica pelo ID."""
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transacoes WHERE id = ?', (id_transacao,))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Transação com ID {id_transacao} excluída com sucesso.")
    else:
        print(f"⚠️ Nenhuma transação encontrada com o ID {id_transacao}.")

    conn.close()


# -------------------------------------------------
# Limpar todas as transações
# -------------------------------------------------
def limpar_todas_transacoes():
    """Remove todas as transações do banco."""
    conn = criar_conexao()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transacoes')
    conn.commit()
    conn.close()

    print("🗑️ Todas as transações foram removidas com sucesso.")

def editar_transacao(id_transacao):
    """
    Edita os campos de uma transação existente.
    Se o usuário apertar Enter sem digitar nada, mantém o valor atual.
    """
    conn = criar_conexao()
    cursor = conn.cursor()

    # Busca a transação atual
    cursor.execute("SELECT * FROM transacoes WHERE id = ?", (id_transacao,))
    row = cursor.fetchone()
    if not row:
        print(f"⚠️ Nenhuma transação encontrada com o ID {id_transacao}.")
        conn.close()
        return

    # row indices: 0=id,1=tipo,2=descricao,3=categoria,4=valor,5=data
    print("\nTransação encontrada:")
    print(f"ID: {row[0]} | Tipo: {row[1]} | Descrição: {row[2]} | Categoria: {row[3]} | Valor: R$ {row[4]:.2f} | Data: {row[5]}")

    # Pergunta pelos novos valores (enter mantém o atual)
    novo_tipo = input(f"Novo tipo (receita/despesa) [{row[1]}]: ").strip().lower() or row[1]
    nova_descricao = input(f"Nova descrição [{row[2]}]: ").strip() or row[2]
    nova_categoria = input(f"Nova categoria [{row[3]}]: ").strip() or row[3]

    # valor: tenta converter, se entrada vazia mantém atual
    entrada_valor = input(f"Novo valor [{row[4]}]: ").strip()
    try:
        novo_valor = float(entrada_valor) if entrada_valor != "" else row[4]
    except ValueError:
        print("Valor inválido. Operação cancelada.")
        conn.close()
        return

    nova_data = input(f"Nova data (AAAA-MM-DD HH:MM:SS) [{row[5]}]: ").strip() or row[5]

    # Atualiza no banco
    cursor.execute("""
        UPDATE transacoes
        SET tipo = ?, descricao = ?, categoria = ?, valor = ?, data = ?
        WHERE id = ?
    """, (novo_tipo, nova_descricao, nova_categoria, novo_valor, nova_data, id_transacao))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Transação ID {id_transacao} atualizada com sucesso.")
    else:
        print("⚠️ Não foi possível atualizar a transação (nenhuma linha afetada).")

    conn.close()