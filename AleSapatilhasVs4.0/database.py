import sqlite3
from datetime import datetime, timedelta

# --- Nome do arquivo do banco de dados ---
DB_NAME = "AleSapatilhasVs4.0db"

def conectar():
    # --- Estabelece a conexão com o banco de dados sqlite3 e habilita o suporte a chaves estrangeiras para garantir a integridade referencial ---
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas():
    # --- Executa a criação de todas as tabelas necessárias, define restrições de dados (check) e configura gatilhos automáticos para controle de estoque ---
    with conectar() as conn:
        cursor = conn.cursor()
        
        # --- Tabela de produtos: armazena informações técnicas, custos, preços de venda e o status atual do inventário ---
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
            status_item TEXT DEFAULT 'Disponível' CHECK(status_item IN ('Disponível', 'Indisponível', 'Esgotado', 'Promocional')),
            foto TEXT DEFAULT '',
            ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # --- Tabela de clientes: registra dados de contato, localização, preferências de tamanho e limites de crédito para vendas a prazo ---
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

        # --- Tabela de vendas: cabeçalho da transação que armazena totais, descontos, formas de pagamento e o vínculo com o cliente ---
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

        # --- Tabela de itens da venda: detalhamento de quais produtos compõem cada venda, registrando o preço praticado no momento da transação ---
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

        # --- Tabela financeiro: centraliza contas a pagar e a receber, permitindo o controle de parcelamento e fluxo de caixa ---
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

        # --- Tabela de pagamentos: registra pagamentos efetuados para vendas ou despesas ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            financeiro_id INTEGER,
            valor_pago REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,
            parcela_referente INTEGER,
            observacao TEXT,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (financeiro_id) REFERENCES financeiro (id)
        )""")
        
        # --- Gatilho de estoque: altera automaticamente o status do produto para 'esgotado' quando a quantidade atinge zero ou menos ---
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_estoque_esgotado
        AFTER UPDATE OF quantidade ON produtos
        BEGIN
            UPDATE produtos SET status_item = 'Esgotado' WHERE id = NEW.id AND quantidade <= 0;
            UPDATE produtos SET status_item = 'Disponível' WHERE id = NEW.id AND quantidade > 0 AND status_item = 'Esgotado';
        END;
        """)

        # --- Atualiza tabela existente para suportar imagem de produto sem quebrar dados já criados ---
        cursor.execute("PRAGMA table_info(produtos)")
        colunas_produtos = [row[1] for row in cursor.fetchall()]
        if "foto" not in colunas_produtos:
            cursor.execute("ALTER TABLE produtos ADD COLUMN foto TEXT DEFAULT ''")
        
        conn.commit()

# --- Funções de produtos ---
def cadastrar_produto(sku, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto=""):
    # --- Insere um novo produto no catálogo. Se o SKU já existir com os mesmos dados, soma a quantidade. Se o SKU existir com atributos diferentes, gera um SKU novo e salva.
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, produto, cor, tamanho, precocusto, precovenda, categoria, material, fornecedor, status_item, foto, quantidade FROM produtos WHERE sku = ?", (sku,))
            existente = cursor.fetchone()
            if existente:
                mesmo_item = (
                    existente[1] == produto and existente[2] == cor and str(existente[3]) == str(tamanho) and
                    float(existente[4]) == float(precocusto) and float(existente[5]) == float(precovenda) and existente[6] == categoria and
                    existente[7] == material and existente[8] == fornecedor and existente[9] == 'Disponível'
                )
                if mesmo_item:
                    cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?", (quantidade, existente[0]))
                    conn.commit()
                    return True
                # Se SKU já existe, mas atributos mudaram, gera um novo SKU único
                base = sku
                suffix = 1
                novo_sku = f"{base}_{suffix}"
                while cursor.execute("SELECT 1 FROM produtos WHERE sku = ?", (novo_sku,)).fetchone():
                    suffix += 1
                    novo_sku = f"{base}_{suffix}"
                sku = novo_sku

            cursor.execute("""
                INSERT INTO produtos (sku, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sku, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def exibir_produtos():
    # --- Recupera a lista completa de produtos cadastrados com seus principais detalhes técnicos e comerciais ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, sku, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, status_item, foto FROM produtos ORDER BY produto ASC")
        return cursor.fetchall()

def atualizar_produto(produto_id, **kwargs):
    # --- Atualiza campos específicos de um produto dinamicamente e registra o horário da última modificação ---
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [produto_id]
        cursor.execute(f"UPDATE produtos SET {campos}, ultima_atualizacao = CURRENT_TIMESTAMP WHERE id = ?", valores)
        conn.commit()

# --- Funções de clientes ---
def cadastrar_cliente(nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite=0):
    # --- Registra um novo cliente no sistema validando a unicidade do cpf e definindo o limite inicial de crédito ---
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone, email, aniversario, tamanho_calcado, endereco_completo, bairro, cidade, cep, observacao, limite_credito)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False

def exibir_clientes():
    # --- Lista todos os clientes cadastrados trazendo informações de contato, status e histórico de cadastro ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, telefone, email, aniversario, tamanho_calcado, endereco_completo, bairro, cidade, cep, observacao, limite_credito, data_cadastro, status_cliente FROM clientes ORDER BY nome ASC")
        return cursor.fetchall()

def atualizar_cliente(cliente_id, **kwargs):
    # --- Modifica os dados de um cliente existente de forma flexível utilizando argumentos nomeados ---
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [cliente_id]
        cursor.execute(f"UPDATE clientes SET {campos} WHERE id = ?", valores)
        conn.commit()

# --- Funções de apoio para vendas e financeiro ---
def atualizar_financeiro(financeiro_id, **kwargs):
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [financeiro_id]
        cursor.execute(f"UPDATE financeiro SET {campos} WHERE id = ?", valores)
        conn.commit()


def buscar_cliente_nome(termo):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ? OR telefone LIKE ? LIMIT 1", (f"%{termo}%", f"%{termo}%"))
        return cursor.fetchone()


def listar_itens():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, status_item, foto FROM produtos WHERE status_item != 'Indisponível' ORDER BY produto ASC")
        return cursor.fetchall()

# --- Movimentações e vendas ---
def realizar_venda_segura(cliente_id, lista_produtos, forma_pgto, parcelas=1, desconto=0):
    # --- Processa uma venda completa: valida o estoque disponível, calcula totais, baixa o inventário e gera as parcelas no financeiro dentro de uma transação segura ---
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # --- Validação de estoque: verifica se cada item da lista possui saldo suficiente antes de prosseguir ---
            for item in lista_produtos:
                cursor.execute("SELECT quantidade, produto FROM produtos WHERE id = ?", (item['id'],))
                res = cursor.fetchone()
                if not res or res[0] < item['qtd']:
                    return False, f"Estoque insuficiente: {res[1] if res else 'Produto não encontrado'}"

            # --- Cálculos financeiros: define o montante bruto e aplica o desconto para chegar ao valor líquido ---
            total_bruto = sum(p['qtd'] * p['preco'] for p in lista_produtos)
            total_liquido = round(total_bruto - desconto, 2)
            
            # --- Registro do cabeçalho: insere os dados gerais da venda para gerar o id de referência ---
            cursor.execute("""INSERT INTO vendas (cliente_id, valor_bruto, desconto, valor_total, forma_pagamento, qtd_parcelas)
                              VALUES (?, ?, ?, ?, ?, ?)""", (cliente_id, total_bruto, desconto, total_liquido, forma_pgto, parcelas))
            venda_id = cursor.lastrowid

            # --- Processamento de itens e estoque: registra cada produto vendido e subtrai a quantidade do inventário ---
            for p in lista_produtos:
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (p['qtd'], p['id']))
                cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                               (venda_id, p['id'], p['qtd'], p['preco'], p['qtd'] * p['preco']))

            # --- Geração de parcelas financeiras: cria registros de receita com vencimentos mensais baseados no número de parcelas ---
            valor_parc = round(total_liquido / parcelas, 2)
            for i in range(parcelas):
                venc = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO financeiro (tipo, venda_id, entidade_nome, descricao, valor, parcela_atual, total_parcelas, data_vencimento, categoria)
                    VALUES ('Receita', ?, (SELECT nome FROM clientes WHERE id=?), ?, ?, ?, ?, ?, 'Venda de Produtos')
                """, (venda_id, cliente_id, f"Venda #{venda_id}", valor_parc, i+1, parcelas, venc))

            conn.commit()
            return True, "Venda finalizada com sucesso!"
        except Exception as e:
            conn.rollback()
            return False, f"Erro ao processar venda: {str(e)}"

# --- Financeiro e relatórios ---
def quitar_titulo_financeiro(financeiro_id, forma_pgto):
    # --- Registra o pagamento de uma conta a pagar ou receber alterando seu status e salvando a data da liquidação ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE financeiro SET status = 'Pago', data_pagamento = ?, forma_pagamento = ? WHERE id = ?", 
                       (hoje, forma_pgto, financeiro_id))

def lancar_despesa(descricao, valor, categoria, vencimento, parcelas=1):
    # --- Cria lançamentos de saída financeira no sistema, permitindo o rateio de valores em várias parcelas mensais ---
    def normalizar_data(data_str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(data_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Formato de data inválido: {data_str}")

    data_inicial = normalizar_data(vencimento)
    with conectar() as conn:
        cursor = conn.cursor()
        valor_parc = round(valor / parcelas, 2)
        for i in range(parcelas):
            data_venc = (data_inicial + timedelta(days=30*i)).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO financeiro (tipo, descricao, valor, parcela_atual, total_parcelas, data_vencimento, categoria, status)
                VALUES ('Despesa', ?, ?, ?, ?, ?, ?, 'Pendente')
            """, (descricao, valor_parc, i+1, parcelas, data_venc, categoria))
        conn.commit()

# --- Funções específicas de Despesas ---
def registrar_pagamento(venda_id, financeiro_id, valor_pago, forma_pagamento, observacao=""):
    # --- Registra um pagamento efetuado para uma venda ou lançamento financeiro ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pagamentos (venda_id, financeiro_id, valor_pago, forma_pagamento, observacao)
            VALUES (?, ?, ?, ?, ?)
        """, (venda_id, financeiro_id, valor_pago, forma_pagamento, observacao))
        return cursor.lastrowid
    # --- Cadastra uma nova despesa registrando todos os dados financeiros e permitindo parcelamento ---
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            valor_parc = round(valor / parcelas, 2)
            
            for i in range(parcelas):
                data_venc = (datetime.strptime(vencimento, "%Y-%m-%d") + timedelta(days=30*i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO financeiro (tipo, entidade_nome, descricao, valor, parcela_atual, total_parcelas, 
                                           data_vencimento, forma_pagamento, categoria, status)
                    VALUES ('Despesa', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (fornecedor, descricao, valor_parc, i+1, parcelas, data_venc, forma_pagamento, categoria, status))
            
            conn.commit()
            return True, "Despesa cadastrada com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar despesa: {str(e)}"

def listar_despesas():
    # --- Retorna todas as despesas registradas no sistema com seus detalhes ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, entidade_nome, descricao, valor, categoria, data_vencimento, 
                   forma_pagamento, status, parcela_atual, total_parcelas
            FROM financeiro 
            WHERE tipo = 'Despesa'
            ORDER BY data_vencimento DESC
        """)
        return cursor.fetchall()

def atualizar_despesa(despesa_id, **kwargs):
    # --- Modifica os dados de uma despesa existente de forma flexível ---
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [despesa_id]
        cursor.execute(f"UPDATE financeiro SET {campos} WHERE id = ? AND tipo = 'Despesa'", valores)
        conn.commit()

def deletar_despesa(despesa_id):
    # --- Remove uma despesa do sistema (incluindo todas as parcelas relacionadas) ---
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            # Busca o número total de parcelas para deletar todas
            cursor.execute("""
                SELECT id, total_parcelas FROM financeiro 
                WHERE id = ? AND tipo = 'Despesa'
            """, (despesa_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return False, "Despesa não encontrada."
            
            # Deleta todas as parcelas da despesa
            cursor.execute("""
                DELETE FROM financeiro 
                WHERE tipo = 'Despesa' AND id IN (
                    SELECT id FROM financeiro 
                    WHERE tipo = 'Despesa' AND descricao = (
                        SELECT descricao FROM financeiro WHERE id = ?
                    ) AND parcela_atual <= (SELECT total_parcelas FROM financeiro WHERE id = ?)
                )
            """, (despesa_id, despesa_id))
            
            conn.commit()
            return True, "Despesa deletada com sucesso!"
    except Exception as e:
        return False, f"Erro ao deletar despesa: {str(e)}"

def buscar_despesa_por_termo(termo):
    # --- Busca despesas por fornecedor ou descrição ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, entidade_nome, descricao, valor, categoria, data_vencimento, 
                   forma_pagamento, status, parcela_atual, total_parcelas
            FROM financeiro 
            WHERE tipo = 'Despesa' AND (
                entidade_nome LIKE ? OR descricao LIKE ?
            )
            ORDER BY data_vencimento DESC
        """, (f"%{termo}%", f"%{termo}%"))
        return cursor.fetchall()

def obter_despesa_por_id(despesa_id):
    # --- Retorna os dados de uma despesa específica ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, entidade_nome, descricao, valor, categoria, data_vencimento, 
                   forma_pagamento, status, parcela_atual, total_parcelas
            FROM financeiro 
            WHERE id = ? AND tipo = 'Despesa'
        """, (despesa_id,))
        return cursor.fetchone()

def dashboard_resumo():
    # --- Gera um panorama rápido contendo alertas de estoque baixo e o montante total de receitas ainda não recebidas ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT produto, quantidade FROM produtos WHERE quantidade < 3 AND status_item != 'Indisponível'")
        alertas = cursor.fetchall()
        
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Receita' AND status = 'Pendente'")
        res = cursor.fetchone()[0]
        
        return {"alertas_estoque": alertas, "total_a_receber": res if res else 0.0}

def relatorio_vendas_geral():
    # --- Realiza um join entre vendas e clientes para gerar um extrato histórico de todas as transações realizadas ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, c.nome, v.valor_total, v.forma_pagamento, v.qtd_parcelas, v.data_venda, v.vendedor, v.status_venda
            FROM vendas v
            JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.data_venda DESC
        """)
        return cursor.fetchall()
    
def fluxo_caixa_mensal(mes, ano):
    # --- Consolida os valores financeiros de um mês específico, separando o que já foi liquidado do que ainda está previsto ---
    with conectar() as conn:
        cursor = conn.cursor()
        filtro = f"{ano}-{str(mes).zfill(2)}%"       

        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN tipo='Receita' AND status='Pago' THEN valor ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo='Despesa' AND status='Pago' THEN valor ELSE 0 END), 0) as saidas,
                COALESCE(SUM(CASE WHEN tipo='Receita' AND status='Pendente' THEN valor ELSE 0 END), 0) as a_receber,
                COALESCE(SUM(CASE WHEN tipo='Despesa' AND status='Pendente' THEN valor ELSE 0 END), 0) as a_pagar
            FROM financeiro 
            WHERE data_vencimento LIKE ? OR data_pagamento LIKE ?
        """, (filtro, filtro))
        
        return cursor.fetchone()

# --- Execução principal ---
if __name__ == "__main__":
    criar_tabelas()
    print("✓ Banco de Dados Ale Sapatilhas Vs4.0 Refatorado e Ativo.")