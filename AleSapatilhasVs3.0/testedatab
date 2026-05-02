import sqlite3
from datetime import datetime

DB_NAME = "AleSapatilhasVs3.0.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()
        
        # 1. Itens (Estoque)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT NOT NULL,
            cor TEXT NOT NULL,
            tamanho INTEGER NOT NULL,
            precocusto REAL,
            precovenda REAL NOT NULL,
            quantidade INTEGER DEFAULT 0 NOT NULL,
            categoria TEXT,
            fornecedor TEXT,
            status_item TEXT DEFAULT 'Disponível'
        )""")

        # 2. Clientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT UNIQUE NOT NULL,
            aniversario DATE,
            tamanho_cliente INTEGER,
            logradouro TEXT,
            numero TEXT,
            bairro TEXT,
            cidade TEXT,
            ponto_referencia TEXT,
            observacao TEXT,
            status_cliente TEXT DEFAULT 'Ativo'
        )""")

        # 3. Vendas (Status movidos para cá - Lógica correta)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            valor_bruto REAL NOT NULL,
            desconto REAL DEFAULT 0,
            valor_total REAL NOT NULL,
            valor_pago REAL DEFAULT 0, 
            comissao_paga REAL,
            forma_pagamento TEXT,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_venda TEXT DEFAULT 'Pendente',
            status_entrega TEXT DEFAULT 'À Entregar',
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )""")

        # 4. Itens da Venda (Apenas dados dos produtos vendidos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES itens (id)
        )""")

        # 5. Financeiro (Gastos da Loja))
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT CHECK(tipo IN ('Fixo', 'Adicional')),
            categoria TEXT,
            data_gasto DATE DEFAULT (date('now'))
        )""")
        conn.commit()

# ==========================================
# --- BUSCAS E FILTROS (Para Interface) ---
# ==========================================

def buscar_produto_nome(nome):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens WHERE produto LIKE ?", (f'%{nome}%',))
        return cursor.fetchall()

def buscar_cliente_nome(nome):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", (f'%{nome}%',))
        return cursor.fetchall()

# ==========================================
# --- GESTÃO DE CLIENTES ---    
# ==========================================

def salvar_cliente(nome, tel, niver, tam, logra, num, bairro, cid, ref, obs, status):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, telefone, aniversario, tamanho_cliente, logradouro, 
            numero, bairro, cidade, ponto_referencia, observacao, status_cliente) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (nome, tel, niver, tam, logra, num, bairro, cid, ref, obs, status))
        conn.commit()

def atualizar_cliente(id_cli, nome, tel, niver, tam, logra, num, bairro, cid, ref, obs, status):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes SET nome=?, telefone=?, aniversario=?, tamanho_cliente=?, logradouro=?, 
            numero=?, bairro=?, cidade=?, ponto_referencia=?, observacao=?, status_cliente=?
            WHERE id=?""", (nome, tel, niver, tam, logra, num, bairro, cid, ref, obs, status, id_cli))
        conn.commit()

def listar_clientes():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
        return cursor.fetchall()

# ==========================================
# --- GESTÃO DE ITENS (PRODUTOS) ---
# ==========================================

def salvar_item(prod, cor, tam, custo, venda, qtd, cat, forn, status):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO itens (produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor, status_item) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
            (prod, cor, tam, custo, venda, qtd, cat, forn, status))
        conn.commit()

def atualizar_item(id_prod, prod, cor, tam, custo, venda, qtd, cat, forn, status):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE itens SET produto=?, cor=?, tamanho=?, precocusto=?, precovenda=?, 
            quantidade=?, categoria=?, fornecedor=?, status_item=? WHERE id=?""",
            (prod, cor, tam, custo, venda, qtd, cat, forn, status, id_prod))
        conn.commit()

def listar_itens():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens ORDER BY produto ASC")
        return cursor.fetchall()

# ==========================================
# --- GESTÃO FINANCEIRA (DESPESAS) ---
# ==========================================

def registrar_despesa(descricao, valor, tipo, categoria):
    """Registra um gasto (Ex: Aluguel, Luz, Limpeza)."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO financeiro (descricao, valor, tipo, categoria) 
            VALUES (?, ?, ?, ?)""", (descricao, valor, tipo, categoria))
        conn.commit()

# ==========================================
# --- LÓGICA DE PDV (VENDAS) ---
# ==========================================

def registrar_venda(cliente_id, lista_produtos, desconto=0, valor_pago=0, forma_pagamento="Dinheiro", perc_comissao=0.05):
    """
    lista_produtos: [(produto_id, qtd, preco_unit)]
    """
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            valor_bruto = sum(p[1] * p[2] for p in lista_produtos)
            valor_total = valor_bruto - desconto
            comissao = valor_total * perc_comissao
            
            cursor.execute("""
                INSERT INTO vendas (cliente_id, valor_bruto, desconto, valor_total, valor_pago, comissao_paga, forma_pagamento) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                (cliente_id, valor_bruto, desconto, valor_total, valor_pago, comissao, forma_pagamento))
            venda_id = cursor.lastrowid

            for p_id, qtd, p_unit in lista_produtos:
                cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)", 
                               (venda_id, p_id, qtd, p_unit))
                # Baixa automática no estoque
                cursor.execute("UPDATE itens SET quantidade = quantidade - ? WHERE id = ?", (qtd, p_id))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao registrar: {e}")
            return False

def editar_venda_completa(venda_id, novos_produtos, novo_desconto, novo_pago, perc_comissao=0.05):
    """Refatorado para recalcular comissão ao editar itens."""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # Estorno de estoque
            cursor.execute("SELECT produto_id, quantidade FROM itens_venda WHERE venda_id = ?", (venda_id,))
            for p_id, qtd in cursor.fetchall():
                cursor.execute("UPDATE itens SET quantidade = quantidade + ? WHERE id = ?", (qtd, p_id))
            
            cursor.execute("DELETE FROM itens_venda WHERE venda_id = ?", (venda_id,))
            
            valor_bruto = sum(p[1] * p[2] for p in novos_produtos)
            valor_total = valor_bruto - novo_desconto
            nova_comissao = valor_total * perc_comissao
            
            cursor.execute("""
                UPDATE vendas SET valor_bruto=?, desconto=?, valor_total=?, valor_pago=?, comissao_paga=? 
                WHERE id=?""", (valor_bruto, novo_desconto, valor_total, novo_pago, nova_comissao, venda_id))
            
            for p_id, qtd, p_unit in novos_produtos:
                cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)", 
                               (venda_id, p_id, qtd, p_unit))
                cursor.execute("UPDATE itens SET quantidade = quantidade - ? WHERE id = ?", (qtd, p_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        
def listar_vendas_controle():
    """Retorna dados simplificados para a Treeview principal."""
    with conectar() as conn:
        cursor = conn.cursor()
        query = """
        SELECT v.id, c.nome, v.valor_total, v.status_venda, v.status_entrega, v.data_venda, v.cliente_id
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
        """
        cursor.execute(query)
        return cursor.fetchall()  
      
def atualizar_status_pedido(venda_id, status_venda, status_entrega):
    """Usado pela JanelaCadastroPedidos para atualizar o fluxo do pedido."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE vendas SET status_venda=?, status_entrega=? 
            WHERE id=?""", (status_venda, status_entrega, venda_id))
        conn.commit()

# ==========================================
# --- RELATÓRIOS ---
# ==========================================

def relatorio_estoque_baixo(limite=5):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT produto, cor, tamanho, quantidade FROM itens WHERE quantidade <= ?", (limite,))
        return cursor.fetchall()

def relatorio_DRE_resumido(mes, ano):
    with conectar() as conn:
        cursor = conn.cursor()
        data_filtro = f"{ano}-{str(mes).zfill(2)}%"

        # Faturamento e Comissões
        cursor.execute("SELECT SUM(valor_total), SUM(comissao_paga) FROM vendas WHERE data_venda LIKE ?", (data_filtro,))
        res_vendas = cursor.fetchone()
        total_vendas = res_vendas[0] or 0
        total_comissoes = res_vendas[1] or 0

        # Custo da Mercadoria Vendida (CMV)
        cursor.execute("""
            SELECT SUM(iv.quantidade * i.precocusto)
            FROM itens_venda iv
            JOIN itens i ON iv.produto_id = i.id
            JOIN vendas v ON iv.venda_id = v.id
            WHERE v.data_venda LIKE ?""", (data_filtro,))
        custo_mercadoria = cursor.fetchone()[0] or 0

        # Despesas da Loja
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE data_gasto LIKE ?", (data_filtro,))
        total_despesas = cursor.fetchone()[0] or 0

        lucro_liquido = total_vendas - custo_mercadoria - total_comissoes - total_despesas

        return {
            "Faturamento Bruto": total_vendas,
            "(-) CMV (Custo)": custo_mercadoria,
            "(-) Comissões": total_comissoes,
            "(-) Despesas Fixas/Adic.": total_despesas,
            "LUCRO LÍQUIDO": lucro_liquido
        }

if __name__ == "__main__":
    criar_tabelas()
    print("Banco de Dados Ale Sapatilhas v4.2 atualizado com sucesso.")