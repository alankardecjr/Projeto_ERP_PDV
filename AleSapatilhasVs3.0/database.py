import sqlite3
from datetime import datetime

DB_NAME = "AleSapatilhasVs3.0db"

def conectar():
    """Retorna uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    """Cria as tabelas do sistema caso não existam."""
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

        # 3. Vendas
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

        # 4. Itens da Venda
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

        # 5. Financeiro (Despesas)
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

def listar_itens():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens ORDER BY produto ASC")
        return cursor.fetchall()

# ==========================================
# --- GESTÃO FINANCEIRA (DESPESAS) ---
# ==========================================

def registrar_despesa(descricao, valor, tipo, categoria, data_gasto=None):
    """Registra uma despesa garantindo o nome correto da coluna de data."""
    with conectar() as conn:
        cursor = conn.cursor()
        if not data_gasto:
            data_gasto = datetime.now().strftime("%Y-%m-%d")
            
        cursor.execute("""
            INSERT INTO financeiro (descricao, valor, tipo, categoria, data_gasto) 
            VALUES (?, ?, ?, ?, ?)""", (descricao, valor, tipo, categoria, data_gasto))
        conn.commit()

def listar_despesas():
    """Retorna todas as despesas para a Treeview."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, descricao, valor, tipo, categoria, data_gasto 
            FROM financeiro 
            ORDER BY data_gasto DESC
        """)
        return cursor.fetchall()

# ==========================================
# --- LÓGICA DE VENDAS E PDV ---
# ==========================================

def registrar_venda(cliente_id, lista_produtos, desconto=0, valor_pago=0, forma_pagamento="Dinheiro", perc_comissao=0.05):
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
                cursor.execute("UPDATE itens SET quantidade = quantidade - ? WHERE id = ?", (qtd, p_id))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False

def relatorio_vendas_geral():
    """Formata os dados das vendas para a visualização na janela principal."""
    with conectar() as conn:
        cursor = conn.cursor()
        query = """
        SELECT v.id, c.nome, v.valor_total, v.valor_pago, v.desconto, v.data_venda, 
               (v.valor_total - v.valor_pago) as saldo, v.status_venda
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.id DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

# ==========================================
# --- RELATÓRIOS (DRE) ---
# ==========================================

def relatorio_DRE_resumido(mes, ano):
    """Calcula o resultado financeiro do mês especificado."""
    with conectar() as conn:
        cursor = conn.cursor()
        data_filtro = f"{ano}-{str(mes).zfill(2)}%"

        # Receita e Comissões
        cursor.execute("SELECT SUM(valor_total), SUM(comissao_paga) FROM vendas WHERE data_venda LIKE ?", (data_filtro,))
        res_vendas = cursor.fetchone()
        total_vendas = res_vendas[0] or 0
        total_comissoes = res_vendas[1] or 0

        # Custo de Mercadoria (CMV) baseado no preço de custo original
        cursor.execute("""
            SELECT SUM(iv.quantidade * i.precocusto)
            FROM itens_venda iv
            JOIN itens i ON iv.produto_id = i.id
            JOIN vendas v ON iv.venda_id = v.id
            WHERE v.data_venda LIKE ?""", (data_filtro,))
        custo_mercadoria = cursor.fetchone()[0] or 0

        # Despesas Fixas e Adicionais
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE data_gasto LIKE ?", (data_filtro,))
        total_despesas = cursor.fetchone()[0] or 0

        lucro_liquido = total_vendas - custo_mercadoria - total_comissoes - total_despesas

        return {
            "Faturamento Bruto": total_vendas,
            "(-) Custo Produtos": custo_mercadoria,
            "(-) Comissões": total_comissoes,
            "(-) Despesas Loja": total_despesas,
            "LUCRO LÍQUIDO": lucro_liquido
        }

if __name__ == "__main__":
    criar_tabelas()
    print("Banco de Dados Ale Sapatilhas v3.0 inicializado.")