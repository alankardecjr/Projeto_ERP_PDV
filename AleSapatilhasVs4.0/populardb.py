import database
import random
from datetime import datetime, timedelta

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas Vs4.0 ===")
    
    # 1. Garantir que as tabelas existam
    database.criar_tabelas()

    # --- 20 CLIENTES ---
    # Ordem: nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite
    clientes_fake = [
        ("Maria Silva", "12345678901", "11988887771", "maria@email.com", "1990-05-15", 35, "Rua das Flores, 10", "Centro", "São Paulo", "01001-000", "Cliente VIP", 500.0),
        ("Ana Oliveira", "23456789012", "11988887772", "ana@email.com", "1985-08-20", 36, "Av. Brasil, 500", "Jardins", "São Paulo", "01430-000", "", 300.0),
        ("Carla Souza", "34567890123", "11988887773", "carla@email.com", "1992-12-10", 37, "Rua Chile, 12", "Mooca", "São Paulo", "03102-000", "Gosta de brilho", 200.0),
        ("Juliana Lima", "45678901234", "11988887774", "ju@email.com", "1988-03-05", 34, "Rua B, 102", "Lapa", "São Paulo", "05001-000", "", 100.0),
        ("Patricia Meira", "56789012345", "11988887775", "paty@email.com", "1995-07-25", 38, "Travessa Paz, 5", "Itaim", "São Paulo", "04531-000", "", 400.0),
        ("Renata Costa", "67890123456", "11988887776", "re@email.com", "1993-01-30", 35, "Rua XV, 20", "Centro", "Curitiba", "80020-000", "", 150.0),
    ]

    for c in clientes_fake:
        if not database.cadastrar_cliente(*c):
            print(f"Aviso: Cliente {c[0]} já existe ou CPF duplicado.")

    # --- 20 PRODUTOS ---
    # Ordem: sku, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor
    produtos_fake = [
        ("SAP-001", "Sapatilha Verniz", "Preta", 35, 40.0, 89.90, 10, "Casual", "Sintético", "Fabrica A"),
        ("SAP-002", "Sapatilha Matelassê", "Bege", 36, 45.0, 95.00, 15, "Clássico", "Napa", "Fabrica B"),
        ("MULE-001", "Mule Bico Fino", "Caramelo", 37, 50.0, 110.00, 8, "Mule", "Couro", "Fabrica A"),
        ("SAP-003", "Sapatilha Boneca", "Vermelha", 34, 42.0, 85.00, 5, "Casual", "Tecido", "Fabrica C"),
        ("SCP-001", "Scarpin Salto Baixo", "Nude", 38, 60.0, 150.00, 12, "Festa", "Verniz", "Fabrica B"),
        ("SAP-004", "Sapatilha Glitter", "Prata", 36, 48.0, 99.00, 7, "Festa", "Glitter", "Fabrica C"),
        ("SAP-005", "Sapatilha Camurça", "Azul", 37, 38.0, 79.90, 20, "Promoção", "Camurça", "Fabrica A"),
        ("RAS-001", "Rasteira Pedraria", "Dourada", 35, 35.0, 75.00, 10, "Verão", "Sintético", "Fabrica D"),
    ]

    for p in produtos_fake:
        if not database.cadastrar_produto(*p):
            print(f"Aviso: Produto {p[1]} já existe ou SKU duplicado.")

    # --- 5 DESPESAS ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    despesas = [
        ("Aluguel da Loja", 2500.00, "Fixa", hoje, 1),
        ("Compra de Estoque Junho", 5000.00, "Variável", hoje, 3),
        ("Energia Elétrica", 320.00, "Fixa", hoje, 1),
        ("Marketing Digital", 450.00, "Variável", hoje, 1),
        ("Internet/Telefone", 120.00, "Fixa", hoje, 1)
    ]
    for d in despesas:
        database.lancar_despesa(*d)

    # --- 10 VENDAS ---
    formas_pag = ["Cartão", "Dinheiro", "Pix"]
    
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE status_cliente = 'Ativo'")
        clientes_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id, precovenda FROM produtos WHERE quantidade > 0")
        produtos_db = [{"id": row[0], "preco": row[1]} for row in cursor.fetchall()]

    if clientes_ids and produtos_db:
        for _ in range(10):
            c_id = random.choice(clientes_ids)
            f_pgto = random.choice(formas_pag)
            parc = 1 if f_pgto != "Cartão" else random.randint(1, 3)
            
            p = random.choice(produtos_db)
            itens_venda = [{"id": p['id'], "qtd": 1, "preco": p['preco']}]
            desconto = random.choice([0, 5, 10.0])
            
            # Chama a função segura que já atualiza estoque e gera financeiro
            database.realizar_venda_segura(c_id, itens_venda, f_pgto, parc, desconto)

    print("\n✅ Banco de Dados Vs4.0 populado com sucesso!")

if __name__ == "__main__":
    popular_banco()