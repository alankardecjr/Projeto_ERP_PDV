import database
import random
from datetime import datetime, timedelta

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas Vs4.0 ===")
    
    # 1. Garantir que as tabelas existam
    database.criar_tabelas()

    # --- 20 CLIENTES (Adicionado CPF fake e Status) ---
    # Estrutura: nome, cpf, tel, email, niver, tam, endereco, bairro, cidade, cep, obs, limite
    clientes_fake = [
        ("Maria Silva", "12345678901", "11988887771", "maria@email.com", "1990-05-15", 35, "Rua das Flores, 10", "Centro", "São Paulo", "01001-000", "Cliente VIP", 500.0),
        ("Ana Oliveira", "23456789012", "11988887772", "ana@email.com", "1985-08-20", 36, "Av. Brasil, 500", "Jardins", "São Paulo", "01430-000", "", 300.0),
        ("Carla Souza", "34567890123", "11988887773", "carla@email.com", "1992-12-10", 37, "Rua Chile, 12", "Mooca", "São Paulo", "03102-000", "Gosta de brilho", 200.0),
        ("Juliana Lima", "45678901234", "11988887774", "ju@email.com", "1988-03-05", 34, "Rua B, 102", "Lapa", "São Paulo", "05001-000", "", 100.0),
        ("Patricia Meira", "56789012345", "11988887775", "paty@email.com", "1995-07-25", 38, "Travessa Paz, 5", "Itaim", "São Paulo", "04531-000", "", 400.0),
        # ... (simplificando para o exemplo, você pode replicar o padrão para os outros 15)
    ]

    for c in clientes_fake:
        try:
            database.cadastrar_cliente(*c)
        except Exception as e:
            print(f"Erro cliente {c[0]}: {e}")

    # --- 20 PRODUTOS (Adicionado SKU único) ---
    # Estrutura: sku, produto, marca, cor, tamanho, precocusto, precovenda, quantidade, categoria, fornecedor
    produtos_fake = [
        ("SAP-001", "Sapatilha Verniz Preta", "Ale Sapatilhas", "Preta", 35, 40.0, 89.90, 10, "Casual", "Fabrica A"),
        ("SAP-002", "Sapatilha Matelassê Bege", "Vizzano", "Bege", 36, 45.0, 95.00, 15, "Clássico", "Fabrica B"),
        ("MULE-001", "Mule Bico Fino Caramelo", "Moleca", "Caramelo", 37, 50.0, 110.00, 8, "Mule", "Fabrica A"),
        ("SAP-003", "Sapatilha Boneca Vermelha", "Beira Rio", "Vermelha", 34, 42.0, 85.00, 5, "Casual", "Fabrica C"),
        ("SCP-001", "Scarpin Nude Salto Baixo", "Vizzano", "Nude", 38, 60.0, 150.00, 12, "Festa", "Fabrica B"),
        ("SAP-004", "Sapatilha Glitter Prata", "Ale Sapatilhas", "Prata", 36, 48.0, 99.00, 7, "Festa", "Fabrica C"),
        ("SAP-005", "Sapatilha Camurça Azul", "Moleca", "Azul", 37, 38.0, 79.90, 20, "Promoção", "Fabrica A"),
        ("RAS-001", "Rasteira Pedraria", "Dakota", "Dourada", 35, 35.0, 75.00, 10, "Verão", "Fabrica D"),
    ]

    for p in produtos_fake:
        try:
            database.cadastrar_produto(*p)
        except Exception as e:
            print(f"Erro produto {p[1]}: {e}")

    # --- 5 DESPESAS (Com parcelas e vencimentos) ---
    # Estrutura: descricao, valor, categoria, vencimento, parcelas
    hoje = datetime.now().strftime("%Y-%m-%d")
    despesas = [
        ("Aluguel da Loja", 2500.00, "Fixa", hoje, 1),
        ("Compra de Estoque Junho", 5000.00, "Variável", hoje, 3),
        ("Energia Elétrica", 320.00, "Fixa", hoje, 1),
        ("Marketing Digital", 450.00, "Variável", hoje, 1),
        ("Internet/Telefone", 120.00, "Fixa", hoje, 1)
    ]
    for d in despesas:
        try:
            database.lancar_despesa(*d)
        except Exception as e:
            print(f"Erro despesa {d[0]}: {e}")

    # --- 10 VENDAS (Usando a lógica realizar_venda_segura) ---
    formas_pag = ["Cartão", "À Vista"]
    # Buscar IDs reais do banco para evitar erros de chave estrangeira
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes")
        clientes_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id, precovenda FROM produtos")
        produtos_db = [{"id": row[0], "preco": row[1]} for row in cursor.fetchall()]

    if clientes_ids and produtos_db:
        for i in range(10):
            c_id = random.choice(clientes_ids)
            f_pgto = random.choice(formas_pag)
            parc = 1 if f_pgto == "À Vista" else random.randint(1, 3)
            
            # Seleciona 1 produto aleatório para a venda
            p = random.choice(produtos_db)
            itens_venda = [{"id": p['id'], "qtd": 1, "preco": p['preco']}]
            
            desconto = random.choice([0, 5, 10])
            
            # realiza_venda_segura(cliente_id, lista_produtos, forma_pgto, parcelas, desconto)
            database.realizar_venda_segura(c_id, itens_venda, f_pgto, parc, desconto)

    print("\n✅ Banco de Dados Vs4.0 populado com sucesso!")
    print("Foram criados Clientes, Produtos, Despesas Parceladas e Vendas com Fluxo Financeiro.")

if __name__ == "__main__":
    popular_banco()