import sqlite3
from datetime import datetime, timedelta

DB_NAME = "AleSapatilhasVs4.0db"

def conectar():
    """Estabelece conexão com o banco de dados e ativa restrições de chave estrangeira."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas():
    """Cria a estrutura de tabelas e automações (triggers) do sistema."""
    with conectar() as conn:
        cursor = conn.cursor()
        
        # 1. ESTOQUE (PRODUTOS)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE, 
            produto TEXT NOT NULL,
            cor TEXT NOT NULL,
            tamanho INTEGER NOT NULL,
            precocusto REAL DEFAULT 0 NOT NULL,
            precovenda REAL NOT NULL,
            quantidade INTEGER DEFAULT 0 NOT NULL,
            categoria TEXT,
            material TEXT,
            fornecedor TEXT,
            status_item TEXT DEFAULT 'Disponível' CHECK(status_item IN ('Disponível', 'Indisponível', 'Esgotado')),
            ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # 2. CLIENTES (CRM)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            telefone TEXT NOT NULL,
            email TEXT,
            aniversario DATE,
            tamanho_calcado INTEGER,
            endereco_completo TEXT,
            bairro TEXT,
            cidade TEXT,
            cep TEXT,
            observacao TEXT,
            limite_credito REAL DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_cliente TEXT DEFAULT 'Ativo' CHECK(status_cliente IN ('Vip', 'Ativo', 'Inativo', 'Bloqueado'))
        )""")

        # 3. VENDAS (HEADER)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            valor_bruto REAL NOT NULL,
            desconto REAL DEFAULT 0,
            valor_total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL, 
            qtd_parcelas INTEGER DEFAULT 1,
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            status_venda TEXT DEFAULT 'Finalizada' CHECK(status_venda IN ('Finalizada', 'Cancelada', 'Pendente')),
            vendedor TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )""")

        # 4. ITENS DA VENDA (DETALHE)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )""")

        # 5. FINANCEIRO INTEGRADO
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Receita', 'Despesa')),
            venda_id INTEGER,
            entidade_nome TEXT, 
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            parcela_atual INTEGER DEFAULT 1,
            total_parcelas INTEGER DEFAULT 1,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            forma_pagamento TEXT,
            categoria TEXT,
            status TEXT DEFAULT 'Pendente' CHECK(status IN ('Pendente', 'Pago', 'Atrasado', 'Cancelado')),
            FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE
        )""")
        
        # TRIGGER: Atualiza status para Esgotado se quantidade for zero
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_estoque_esgotado
        AFTER UPDATE OF quantidade ON produtos
        BEGIN
            UPDATE produtos SET status_item = 'Esgotado' WHERE id = NEW.id AND quantidade <= 0;
            UPDATE produtos SET status_item = 'Disponível' WHERE id = NEW.id AND quantidade > 0;
        END;
        """)
        
        conn.commit()

# ==========================================
# FUNÇÕES DE ESTOQUE E CLIENTES
# ==========================================

def cadastrar_produto(sku, produto, marca, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor):
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (sku, produto, marca, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sku, produto, marca, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor))
            return True
    except sqlite3.IntegrityError:
        return False
    
def exibir_produtos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, sku, produto, marca, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor, status_item FROM produtos")
        return cursor.fetchall()
    
def atualizar_produto(produto_id, **kwargs):
    """Atualiza informações do produto de forma flexível."""
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [produto_id]
        cursor.execute(f"UPDATE produtos SET {campos} WHERE id = ?", valores)
        conn.commit()      

def cadastrar_cliente(nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite=0):
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone, email, aniversario, tamanho_calcado, endereco_completo, bairro, cidade, cep, observacao, limite_credito)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite))
            return True
    except sqlite3.IntegrityError:
        return False

def exibir_clientes():
    """Exibe clientes com ID e campos necessários para a interface."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cpf, telefone, email, aniversario, 
                   tamanho_calcado, endereco_completo, bairro, cidade, 
                   cep, observacao, limite_credito, data_cadastro, status_cliente 
            FROM clientes
        """)
        return cursor.fetchall()
    
def atualizar_cliente(cliente_id, **kwargs):
    """Atualiza informações do cliente de forma flexível."""
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [cliente_id]
        cursor.execute(f"UPDATE clientes SET {campos} WHERE id = ?", valores)
        conn.commit()

# ==========================================
# LÓGICA DE VENDAS E FINANCEIRO
# ==========================================

def realizar_venda_segura(cliente_id, lista_produtos, forma_pgto, parcelas=1, desconto=0):
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # 1. Validação de Estoque
            for item in lista_produtos:
                cursor.execute("SELECT quantidade, produto FROM produtos WHERE id = ?", (item['id'],))
                res = cursor.fetchone()
                if not res:
                    return False, f"Produto ID {item['id']} não encontrado."
                if res[0] < item['qtd']:
                    return False, f"Estoque insuficiente para {res[1]}. Disponível: {res[0]}"

            # 2. Registrar Venda
            total_bruto = sum(p['qtd'] * p['preco'] for p in lista_produtos)
            total_liquido = total_bruto - desconto
            
            cursor.execute("""INSERT INTO vendas (cliente_id, valor_bruto, desconto, valor_total, forma_pagamento, qtd_parcelas)
                              VALUES (?, ?, ?, ?, ?, ?)""", (cliente_id, total_bruto, desconto, total_liquido, forma_pgto, parcelas))
            venda_id = cursor.lastrowid

            # 3. Baixar Estoque e Registrar Itens
            for p in lista_produtos:
                subtotal = p['qtd'] * p['preco']
                # Nota: Removi o campo 'ultima_atualizacao' do UPDATE manual, 
                # pois o DEFAULT CURRENT_TIMESTAMP no CREATE TABLE já cuida disso se você configurar o campo como DEFAULT.
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (p['qtd'], p['id']))
                cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                               (venda_id, p['id'], p['qtd'], p['preco'], subtotal))

            # 4. Gerar Financeiro
            valor_parc = total_liquido / parcelas
            for i in range(parcelas):
                venc = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO financeiro (tipo, venda_id, entidade_nome, descricao, valor, parcela_atual, total_parcelas, data_vencimento, categoria)
                    VALUES ('Receita', ?, (SELECT nome FROM clientes WHERE id=?), ?, ?, ?, ?, ?, 'Venda de Produtos')
                """, (venda_id, cliente_id, f"Venda #{venda_id}", valor_parc, i+1, parcelas, venc))

            conn.commit()
            return True, "Venda realizada com sucesso"
        except Exception as e:
            conn.rollback()
            return False, f"Erro Crítico: {str(e)}"

def quitar_titulo_financeiro(financeiro_id, forma_pgto):
    """Marca uma parcela como paga e registra a data e forma."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE financeiro 
            SET status = 'Pago', data_pagamento = ?, forma_pagamento = ? 
            WHERE id = ?""", (hoje, forma_pgto, financeiro_id))
        conn.commit()

# ==========================================
# RELATÓRIOS E DASHBOARD
# ==========================================

# Adicione isso ao seu arquivo database.py

def relatorio_vendas_geral():
    """Retorna o histórico de vendas com o nome do cliente vinculado."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, c.nome, v.valor_total, v.forma_pagamento, v.qtd_parcelas, v.data_venda, v.vendedor, v.status_venda
            FROM vendas v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_venda DESC
        """)
        return cursor.fetchall()

def lancar_despesa(descricao, valor, categoria, vencimento, parcelas=1):
    """Lança uma conta a pagar (Ex: Aluguel, Luz, Fornecedor)."""
    with conectar() as conn:
        cursor = conn.cursor()
        valor_parc = valor / parcelas
        for i in range(parcelas):
            data_venc = (datetime.strptime(vencimento, "%Y-%m-%d") + timedelta(days=30*i)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO financeiro (tipo, descricao, valor, parcela_atual, total_parcelas, data_vencimento, categoria, status)
                VALUES ('Despesa', ?, ?, ?, ?, ?, ?, 'Pendente')
            """, (descricao, valor_parc, i+1, parcelas, data_venc, categoria))
        conn.commit()

def fluxo_caixa_mensal(mes, ano):
    """Relatório Profissional: Comparativo Realizado vs Pendente."""
    with conectar() as conn:
        cursor = conn.cursor()
        filtro = f"{ano}-{str(mes).zfill(2)}%"
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo='Receita' AND status='Pago' THEN valor ELSE 0 END) as entradas,
                SUM(CASE WHEN tipo='Despesa' AND status='Pago' THEN valor ELSE 0 END) as saidas,
                SUM(CASE WHEN tipo='Receita' AND status='Pendente' THEN valor ELSE 0 END) as a_receber,
                SUM(CASE WHEN tipo='Despesa' AND status='Pendente' THEN valor ELSE 0 END) as a_pagar
            FROM financeiro 
            WHERE data_vencimento LIKE ? OR data_pagamento LIKE ?
        """, (filtro, filtro))
        
        return cursor.fetchone()

def dashboard_resumo():
    """Dados consolidados para a Home do ERP."""
    with conectar() as conn:
        cursor = conn.cursor()
        
        # Alerta de Estoque Baixo
        cursor.execute("SELECT produto, quantidade FROM produtos WHERE quantidade < 3 AND status_item != 'Indisponível'")
        alertas = cursor.fetchall()
        
        # Total Pendente (Prevenção de None)
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Receita' AND status = 'Pendente'")
        a_receber = cursor.fetchone()[0] or 0.0
        
        return {"alertas_estoque": alertas, "total_a_receber": a_receber}

if __name__ == "__main__":
    criar_tabelas()
    print("Core Ale Sapatilhas ERP Professional Vs4.0 - Database Ativo.")