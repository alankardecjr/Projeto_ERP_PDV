import sqlite3
from datetime import datetime, timedelta

# --- Configuração do Banco de Dados ---
DB_NAME = "AleSapatilhasVs4.4db"

def conectar():
    """Estabelece a conexão com suporte a chaves estrangeiras[cite: 1]."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def criar_tabelas():
    """Cria a estrutura completa do ERP com foco em rastreabilidade financeira[cite: 1]."""
    with conectar() as conn:
        cursor = conn.cursor()
        
        # --- PRODUTOS ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            tipo TEXT CHECK(tipo IN ('Calçados', 'Confecções')) DEFAULT 'Calçados',
            produto TEXT NOT NULL,
            cor TEXT NOT NULL,
            tamanho INTEGER NOT NULL,
            precocusto REAL DEFAULT 0,
            precovenda REAL NOT NULL,
            quantidade INTEGER DEFAULT 0,
            categoria TEXT,
            material TEXT,
            fornecedor TEXT,
            status_item TEXT DEFAULT 'Disponível',
            foto TEXT DEFAULT '',
            ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # --- Tabela de clientes: registra dados de contato, localização, preferências de tamanho e limites de crédito para vendas a prazo ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Cliente', 'Fornecedor')) DEFAULT 'Cliente',
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

       # 3. INTERAÇÕES (Novo CRM)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente_interacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data_interacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo_contato TEXT CHECK(tipo_contato IN ('WhatsApp', 'Telefone', 'E-mail', 'Presencial')),
            assunto TEXT, 
            detalhes TEXT,
            vendedor_responsavel TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )""")

        # --- VENDAS ---
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

        # --- ITENS DA VENDA ---
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

        # --- FINANCEIRO (Refatorado para Recorrência e Pagamentos Parciais) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Receita', 'Despesa')),
            venda_id INTEGER,
            cliente_id INTEGER,
            id_agrupador INTEGER, 
            entidade_nome TEXT, 
            descricao TEXT,
            valor REAL NOT NULL,            -- Valor líquido esperado da parcela
            valor_base REAL,                 -- Valor original sem encargos/descontos
            valor_pago REAL DEFAULT 0,       -- Suporte a pagamento parcial[cite: 1]
            encargos REAL DEFAULT 0,
            descontos REAL DEFAULT 0,
            forma_pagamento TEXT,
            recorrencia TEXT DEFAULT 'Não Recorrente',
            total_parcelas INTEGER DEFAULT 1,
            parcela_atual INTEGER DEFAULT 1,
            data_vencimento DATE NOT NULL,   -- Data específica da parcela[cite: 1]
            data_pagamento DATE,
            categoria TEXT,
            status TEXT DEFAULT 'Pendente' CHECK(status IN ('Pendente', 'Pago', 'Atrasado', 'Cancelado')),
            data_lancamento DATE DEFAULT CURRENT_DATE,
            tipo_encargos TEXT DEFAULT 'Valor Fixo',
            valor_encargos REAL DEFAULT 0,
            tipo_descontos TEXT DEFAULT 'Valor Fixo',
            valor_descontos REAL DEFAULT 0,
            FOREIGN KEY (venda_id) REFERENCES vendas (id) ON DELETE CASCADE
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)   
                            )""")

        # --- PAGAMENTOS (Log de auditoria) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            financeiro_id INTEGER,
            valor_pago REAL NOT NULL,
            juros_pagos REAL DEFAULT 0,
            descontos_pagos REAL DEFAULT 0,
            forma_pagamento TEXT NOT NULL,
            data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,
            conta_bancaria TEXT,
            observacao TEXT,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (financeiro_id) REFERENCES financeiro (id)
        )""")

        # Trigger para Status de Estoque
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_estoque_status
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
def cadastrar_produto(sku, tipo, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto=""):
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
                INSERT INTO produtos (sku, tipo, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sku, tipo, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def exibir_produtos():
    # --- Recupera a lista completa de produtos cadastrados com seus principais detalhes técnicos e comerciais ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, sku, tipo, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, status_item, foto FROM produtos ORDER BY produto ASC")
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
                INSERT INTO clientes (tipo, nome, cpf, telefone, email, aniversario, tamanho_calcado, endereco_completo, bairro, cidade, cep, observacao, limite_credito)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ('Cliente', nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite))
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return False
        
def exibir_clientes():
    # --- Lista todos os clientes cadastrados trazendo informações de contato, status e histórico de cadastro ---
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, nome, cpf, telefone, email, aniversario, tamanho_calcado, endereco_completo, bairro, cidade, cep, observacao, limite_credito, data_cadastro, status_cliente FROM clientes ORDER BY nome ASC")
        return cursor.fetchall()

def atualizar_cliente(cliente_id, **kwargs):
    # --- Modifica os dados de um cliente existente de forma flexível utilizando argumentos nomeados ---
    with conectar() as conn:
        cursor = conn.cursor()
        campos = ", ".join(f"{k} = ?" for k in kwargs.keys())
        valores = list(kwargs.values()) + [cliente_id]
        cursor.execute(f"UPDATE clientes SET {campos} WHERE id = ?", valores)
        conn.commit()

def registrar_interacao(cliente_id, tipo, assunto, detalhes, vendedor):
    with conectar() as conn:
        conn.execute("INSERT INTO cliente_interacoes (cliente_id, tipo_contato, assunto, detalhes, vendedor_responsavel) VALUES (?,?,?,?,?)",
                     (cliente_id, tipo, assunto, detalhes, vendedor))

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


# --- MOTORES DE CÁLCULO (AUXILIARES) ---

def adicionar_meses(data_obj, meses):
    ano = data_obj.year + (data_obj.month + meses - 1) // 12
    mes = (data_obj.month + meses - 1) % 12 + 1
    ultimo_dia = [31, 29 if ano % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes-1]
    dia = min(data_obj.day, ultimo_dia)
    return datetime(ano, mes, dia)

def calcular_valor_com_ajustes(valor_base, t_enc, v_enc, t_desc, v_desc):
    enc = v_enc if t_enc == 'Valor Fixo' else round(valor_base * (v_enc / 100), 2)
    des = v_desc if t_desc == 'Valor Fixo' else round(valor_base * (v_desc / 100), 2)
    return round(valor_base + enc - des, 2), enc, des

def realizar_venda_crediario(cliente_id, lista_produtos, parcelas, desc_venda=0):
    """Lógica de venda que alimenta a tabela 'receitas' via crediário."""
    with conectar() as conn:
        cursor = conn.cursor()
        total_bruto = sum(p['qtd'] * p['preco'] for p in lista_produtos)
        total_liquido = total_bruto - desc_venda
        
        cursor.execute("INSERT INTO vendas (cliente_id, valor_bruto, desconto, valor_total, forma_pagamento, qtd_parcelas) VALUES (?,?,?,?,?,?)",
                       (cliente_id, total_bruto, desc_venda, total_liquido, 'Crediário', parcelas))
        venda_id = cursor.lastrowid

        valor_parc = round(total_liquido / parcelas, 2)
        for i in range(parcelas):
            venc = adicionar_meses(datetime.now(), 'Mensal', i).strftime("%Y-%m-%d")
            cursor.execute("""INSERT INTO receitas (venda_id, cliente_id, descricao, valor_base, valor_esperado, data_vencimento, parcela_atual, total_parcelas) 
                              VALUES (?,?,?,?,?,?,?,?)""", 
                           (venda_id, cliente_id, f"Parcela {i+1}/{parcelas} - Venda #{venda_id}", valor_parc, valor_parc, venc, i+1, parcelas))
        conn.commit()

def realizar_venda_segura(cliente_id, lista_produtos, forma_pgto, parcelas=1, desconto_total=0):
    """Executa a venda e projeta as parcelas nas datas específicas de fluxo de caixa[cite: 1]."""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            # --- Validação de estoque: verifica se cada item da lista possui saldo suficiente antes de prosseguir ---
            for item in lista_produtos:
                cursor.execute("SELECT quantidade, produto FROM produtos WHERE id = ?", (item['id'],))
                res = cursor.fetchone()
                if not res or res[0] < item['qtd']:
                    return False, f"Estoque insuficiente: {res[1] if res else 'Produto não encontrado'}"
           
            total_bruto = sum(p['qtd'] * p['preco'] for p in lista_produtos)
            total_liquido = round(total_bruto - desconto_total, 2)
            
            # Registro da Venda
            cursor.execute("""INSERT INTO vendas (cliente_id, valor_bruto, desconto, valor_total, forma_pagamento, qtd_parcelas)
                              VALUES (?, ?, ?, ?, ?, ?)""", (cliente_id, total_bruto, desconto_total, total_liquido, forma_pgto, parcelas))
            venda_id = cursor.lastrowid

            # --- Processamento de itens e estoque: registra cada produto vendido e subtrai a quantidade do inventário ---
            for p in lista_produtos:
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (p['qtd'], p['id']))
                cursor.execute("INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                               (venda_id, p['id'], p['qtd'], p['preco'], p['qtd'] * p['preco']))

            # Lançamento das Parcelas Recorrentes
            valor_parcela = round(total_liquido / parcelas, 2)
            for i in range(parcelas):
                if i == parcelas - 1: # Ajuste de centavos na última parcela
                    valor_parcela = round(total_liquido - (valor_parcela * (parcelas - 1)), 2)
                
                vencimento = adicionar_meses(datetime.now(), i).strftime("%Y-%m-%d")
                
                cursor.execute("""
                    INSERT INTO financeiro (
                        tipo, venda_id, id_agrupador, entidade_nome, descricao, valor, valor_base, 
                        parcela_atual, total_parcelas, data_vencimento, categoria, recorrencia
                    ) VALUES ('Receita', ?, ?, (SELECT nome FROM clientes WHERE id=?), ?, ?, ?, ?, ?, ?, 'Venda', 'Parcelado')
                """, (venda_id, venda_id, cliente_id, f"Venda #{venda_id} - Parcela {i+1}/{parcelas}", 
                      valor_parcela, valor_parcela, i+1, parcelas, vencimento))

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
            data_venc = adicionar_meses(data_inicial, i).strftime("%Y-%m-%d")
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

def cadastrar_despesa(fornecedor, descricao, categoria, valor, recorrencia, vencimento, forma_pagamento, status, parcelas=1,
                       data_lancamento=None, data_pagamento=None, tipo_encargos='Valor Fixo', valor_encargos=0.0,
                       tipo_descontos='Valor Fixo', valor_descontos=0.0, valor_base=None):
    # --- Insere uma nova despesa no financeiro com recorrência e/ou parcelamento mensal ---
    def normalizar_data(data_str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(data_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Formato de data inválido: {data_str}")

    data_inicial = normalizar_data(vencimento)
    if valor_base is None:
        valor_base = valor

    if tipo_encargos == 'Porcentagem':
        encargos_total = round(valor_base * (valor_encargos / 100), 2)
    else:
        encargos_total = round(valor_encargos, 2)

    if tipo_descontos == 'Porcentagem':
        descontos_total = round(valor_base * (valor_descontos / 100), 2)
    else:
        descontos_total = round(valor_descontos, 2)

    valor_final = round(valor_base + encargos_total - descontos_total, 2)
    if recorrencia == 'Parcelar':
        valor_parc = round(valor_final / parcelas, 2)
    else:
        valor_parc = valor_final

    if data_lancamento is None:
        data_lancamento = datetime.now().strftime('%Y-%m-%d')
    else:
        data_lancamento = normalizar_data(data_lancamento).strftime('%Y-%m-%d')

    if data_pagamento:
        data_pagamento = normalizar_data(data_pagamento).strftime('%Y-%m-%d')

    with conectar() as conn:
        cursor = conn.cursor()
        for i in range(parcelas):
            data_venc = adicionar_meses(data_inicial, i).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO financeiro (tipo, entidade_nome, descricao, valor, valor_base, parcela_atual, total_parcelas,
                                       data_vencimento, data_pagamento, forma_pagamento, categoria, status, recorrencia,
                                       data_lancamento, tipo_encargos, valor_encargos, tipo_descontos, valor_descontos)
                VALUES ('Despesa', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fornecedor, descricao, valor_parc, valor_base, i+1, parcelas, data_venc, data_pagamento,
                   forma_pagamento, categoria, status, recorrencia, data_lancamento, tipo_encargos,
                   valor_encargos, tipo_descontos, valor_descontos))
        conn.commit()
        return True, "Despesa cadastrada com sucesso!"

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
    """Consolida as parcelas nas datas específicas para visualização no fluxo de caixa[cite: 1]."""
    with conectar() as conn:
        cursor = conn.cursor()
        filtro = f"{ano}-{str(mes).zfill(2)}%"
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN tipo='Receita' AND status='Pago' THEN valor_pago ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo='Despesa' AND status='Pago' THEN valor_pago ELSE 0 END), 0) as saidas,
                COALESCE(SUM(CASE WHEN tipo='Receita' AND status='Pendente' THEN (valor - valor_pago) ELSE 0 END), 0) as a_receber,
                COALESCE(SUM(CASE WHEN tipo='Despesa' AND status='Pendente' THEN (valor - valor_pago) ELSE 0 END), 0) as a_pagar
            FROM financeiro 
            WHERE data_vencimento LIKE ? OR data_pagamento LIKE ?
        """, (filtro, filtro))
        return cursor.fetchone()

def listar_itens():
    """Recupera produtos para o checkout[cite: 1]."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, produto, cor, tamanho, precocusto, precovenda, quantidade FROM produtos WHERE status_item != 'Indisponível'")
        return cursor.fetchall()

if __name__ == "__main__":
    criar_tabelas()
    print("✓ Banco de Dados Ale Sapatilhas Vs4.0 - Completo e Ativo.")