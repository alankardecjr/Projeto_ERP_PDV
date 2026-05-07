import database
import random
import os
from datetime import datetime, timedelta

# Use este script para criar uma base de dados de teste com clientes, produtos, vendas e despesas.
# Comentários pessoais ficam aqui para lembrar que esse arquivo é o cenário de teste do sistema.

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas Vs4.0 ===")
    database.criar_tabelas()

    # --- 20 CLIENTES TESTE ---
    clientes_fake = [
        ("Maria Silva", "12345678901", "11988887771", "maria.silva@email.com", "1990-05-15", 35, "Rua das Flores, 10", "Centro", "São Paulo", "01001-000", "Cliente VIP adora novidades", 500.0),
        ("Ana Oliveira", "23456789012", "11988887772", "ana.oliveira@email.com", "1985-08-20", 36, "Av. Brasil, 500", "Jardins", "São Paulo", "01430-000", "Pagamento sempre em dia", 300.0),
        ("Carla Souza", "34567890123", "11988887773", "carla.souza@email.com", "1992-12-10", 37, "Rua Chile, 12", "Mooca", "São Paulo", "03102-000", "Gosta de cores vivas", 200.0),
        ("Juliana Lima", "45678901234", "11988887774", "juliana.lima@email.com", "1988-03-05", 34, "Rua B, 102", "Lapa", "São Paulo", "05001-000", "Quer novidades toda semana", 100.0),
        ("Patrícia Meira", "56789012345", "11988887775", "patricia.meira@email.com", "1995-07-25", 38, "Travessa Paz, 5", "Itaim", "São Paulo", "04531-000", "Cliente fiel", 400.0),
        ("Renata Costa", "67890123456", "11988887776", "renata.costa@email.com", "1993-01-30", 35, "Rua XV, 20", "Centro", "Curitiba", "80020-000", "Trabalha no centro", 150.0),
        ("Natália Ferreira", "78901234567", "11988887777", "natalia.ferreira@email.com", "1989-11-12", 36, "Rua das Laranjeiras, 44", "Batel", "Curitiba", "80420-000", "Compra presentes para amigas", 250.0),
        ("Bianca Santos", "89012345678", "11988887778", "bianca.santos@email.com", "1991-09-02", 37, "Av. Paulista, 1000", "Bela Vista", "São Paulo", "01310-000", "Adora sapatos exclusivos", 350.0),
        ("Daniela Rocha", "90123456789", "11988887779", "daniela.rocha@email.com", "1987-06-18", 39, "Rua Augusta, 150", "Consolação", "São Paulo", "01305-000", "Gosta de atendimento personalizado", 180.0),
        ("Flávia Almeida", "01234567890", "11988887780", "flavia.almeida@email.com", "1994-02-22", 38, "Rua 7 de Abril, 123", "Centro", "Campinas", "13010-000", "Prefere pagamentos à vista", 220.0),
        ("Bruna Mendes", "11234567890", "11988887781", "bruna.mendes@email.com", "1996-01-14", 34, "Rua das Palmeiras, 78", "Vila Mariana", "São Paulo", "04105-000", "Curte promoções", 280.0),
        ("Fernanda Alves", "12234567890", "11988887782", "fernanda.alves@email.com", "1986-04-09", 36, "Av. Ipiranga, 800", "Higienópolis", "São Paulo", "01222-000", "Gosta de peças clássicas", 320.0),
        ("Juliana Costa", "13234567890", "11988887783", "juliana.costa@email.com", "1982-10-28", 37, "Rua do Comércio, 30", "Centro", "Porto Alegre", "90010-000", "Compra para mães e filhas", 260.0),
        ("Patrícia Souza", "14234567890", "11988887784", "patricia.souza@email.com", "1999-12-05", 35, "Rua das Acácias, 22", "Área 14", "Florianópolis", "88020-000", "Cliente nova loja", 210.0),
        ("Aline Martins", "15234567890", "11988887785", "aline.martins@email.com", "1998-09-19", 36, "Av. Beira Mar, 210", "Meia Praia", "Itapema", "88330-000", "Gosta de peças confortáveis", 240.0),
        ("Camila Pereira", "16234567890", "11988887786", "camila.pereira@email.com", "1991-04-01", 34, "Rua dos Jasmins, 118", "Jardim", "Belo Horizonte", "30170-000", "Compra para o trabalho", 190.0),
        ("Débora Gomes", "17234567890", "11988887787", "debora.gomes@email.com", "1997-12-12", 37, "Rua das Margaridas, 64", "Sala", "Rio de Janeiro", "20040-000", "Prefere cores neutras", 270.0),
        ("Lorena Rocha", "18234567890", "11988887788", "lorena.rocha@email.com", "1984-07-08", 38, "Rua do Mercado, 99", "Copacabana", "Rio de Janeiro", "22040-000", "Cliente festa", 430.0),
        ("Simone Ribeiro", "19234567890", "11988887789", "simone.ribeiro@email.com", "1990-03-17", 39, "Av. Atlântica, 500", "Copacabana", "Rio de Janeiro", "22070-000", "Quer sapatos confortáveis", 310.0),
        ("Tatiana Nunes", "20234567890", "11988887790", "tatiana.nunes@email.com", "1983-08-27", 36, "Rua das Gaivotas, 14", "Maresias", "São Sebastião", "11600-000", "Cliente de praia", 290.0),
    ]

    for cliente in clientes_fake:
        if not database.cadastrar_cliente(*cliente):
            print(f"Aviso: Cliente {cliente[0]} já existe ou CPF duplicado.")

    # --- 10 PRODUTOS COM FOTOS ---
    produtos_fake = [
        ("SAP-001", "Sapatilha Verniz", "Preta", 35, 40.0, 89.90, 18, "Casual", "Sintético", "Fábrica A", "images/produto01.jpg"),
        ("SAP-002", "Sapatilha Matelassê", "Bege", 36, 45.0, 95.00, 20, "Clássico", "Napa", "Fábrica B", "images/produto02.jpg"),
        ("MUL-001", "Mule Bico Fino", "Caramelo", 37, 50.0, 110.00, 12, "Mule", "Couro", "Fábrica A", "images/produto03.jpg"),
        ("SAP-003", "Sapatilha Boneca", "Vermelha", 34, 42.0, 85.00, 14, "Casual", "Tecido", "Fábrica C", "images/produto04.jpg"),
        ("SCP-001", "Scarpin Salto Baixo", "Nude", 38, 60.0, 150.00, 10, "Festa", "Verniz", "Fábrica B", "images/produto05.jpg"),
        ("SAP-004", "Sapatilha Glitter", "Prata", 36, 48.0, 99.00, 9, "Festa", "Glitter", "Fábrica C", "images/produto06.jpg"),
        ("SAP-005", "Sapatilha Camurça", "Azul", 37, 38.0, 79.90, 22, "Promoção", "Camurça", "Fábrica A", "images/produto07.jpg"),
        ("RAS-001", "Rasteira Pedraria", "Dourada", 35, 35.0, 75.00, 16, "Verão", "Sintético", "Fábrica D", "images/produto08.jpg"),
        ("SAP-006", "Sapatilha Animal Print", "Onça", 36, 44.0, 92.00, 13, "Trendy", "PU", "Fábrica E", "images/produto09.jpg"),
        ("TEN-001", "Tênis Casual", "Branco", 38, 55.0, 129.90, 11, "Esportivo", "Couro Sintético", "Fábrica F", "images/produto10.jpg"),
    ]

    for produto in produtos_fake:
        if not database.cadastrar_produto(*produto):
            print(f"Aviso: Produto {produto[1]} já existe ou SKU duplicado.")

    # --- 15 DESPESAS FIXAS ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    despesas_fixas = [
        ("Fornecedor Genérico", "Aluguel", "Infraestrutura", 3200.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Energia Elétrica", "Infraestrutura", 520.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Água", "Infraestrutura", 180.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Internet/Telefone", "Infraestrutura", 190.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Segurança", "Infraestrutura", 420.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Limpeza", "Infraestrutura", 260.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Salário Administrativo", "Salários", 3200.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Contabilidade", "Outros", 650.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Seguro da Loja", "Outros", 250.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Licenças de Software", "Outros", 180.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Manutenção de Equipamentos", "Infraestrutura", 230.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Marketing Mensal", "Marketing", 490.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Assinatura de Sistemas", "Outros", 140.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Impostos Municipais", "Impostos", 380.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Taxas de Cartão", "Outros", 290.00, "Fixa Mensal", hoje, "Dinheiro", "Pendente", 1),
    ]
    for despesa in despesas_fixas:
        sucesso, msg = database.cadastrar_despesa(*despesa)
        if not sucesso:
            print(f"Aviso despesa: {msg}")

    # --- 8 DESPESAS VARIÁVEIS ---
    despesas_variaveis = [
        ("Fornecedor Genérico", "Compra de Mercadorias", "Compra Mercadoria", 7200.00, "Parcelar", hoje, "Cartão de Crédito", "Pendente", 3),
        ("Fornecedor Genérico", "Compra de Insumos", "Compra Mercadoria", 1800.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Frete de Recebimento", "Compra Mercadoria", 420.00, "Não Recorrente", hoje, "Pix", "Pendente", 1),
        ("Fornecedor Genérico", "Material de Embalagem", "Compra Mercadoria", 220.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Peças de Reposição", "Infraestrutura", 310.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Comissão de Vendedores", "Salários", 360.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Ajuste de Estoque", "Outros", 780.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
        ("Fornecedor Genérico", "Brindes para Clientes", "Marketing", 210.00, "Não Recorrente", hoje, "Dinheiro", "Pendente", 1),
    ]
    for despesa in despesas_variaveis:
        sucesso, msg = database.cadastrar_despesa(*despesa)
        if not sucesso:
            print(f"Aviso despesa: {msg}")

    # --- 8 VENDAS DE TESTE ---
    formas_pag = ["Cartão", "Dinheiro", "Pix"]
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE status_cliente = 'Ativo'")
        clientes_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id, precovenda, quantidade FROM produtos WHERE quantidade > 0")
        produtos_db = [
            {"id": row[0], "preco": row[1], "qtd": row[2]} for row in cursor.fetchall()
        ]

    if clientes_ids and produtos_db:
        for venda_index in range(1, 9):
            cliente_id = random.choice(clientes_ids)
            forma = random.choice(formas_pag)
            parcelas = 1 if forma != "Cartão" else random.randint(1, 3)
            quantidade_item = random.randint(1, 3)
            produto = random.choice([p for p in produtos_db if p["qtd"] >= quantidade_item])
            desconto = random.choice([0, 10, 15.0])

            itens_venda = [{"id": produto["id"], "qtd": quantidade_item, "preco": produto["preco"]}]
            resultado, msg = database.realizar_venda_segura(cliente_id, itens_venda, forma, parcelas, desconto)
            if not resultado:
                print(f"Venda {venda_index} não registrada: {msg}")

    # --- PAGAMENTOS DE TESTE ---
    # Simular pagamentos para algumas vendas
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, valor_total FROM vendas LIMIT 5")
        vendas_para_pagar = cursor.fetchall()
        
        for venda in vendas_para_pagar:
            venda_id, valor_total = venda
            valor_pago = valor_total  # Pagamento total
            forma_pag = random.choice(["Dinheiro", "Cartão de Crédito", "Pix"])
            database.registrar_pagamento(venda_id, None, valor_pago, forma_pag, f"Pagamento da venda #{venda_id}")

    print("\n✅ Banco de Dados Vs4.0 populado com teste completo!")


if __name__ == "__main__":
    popular_banco()
