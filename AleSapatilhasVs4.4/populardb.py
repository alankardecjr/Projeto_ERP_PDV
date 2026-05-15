import database
import random
from datetime import datetime

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas Vs4.4 ===")
    database.criar_tabelas()

    # --- Limpeza Controlada ---
    with database.conectar() as conn:
        cursor = conn.cursor()
        tabelas = ["pagamentos", "financeiro", "itens_venda", "vendas", "produtos", "clientes", "cliente_interacoes"]
        for tabela in tabelas:
            cursor.execute(f"DELETE FROM {tabela}")
        cursor.execute("DELETE FROM sqlite_sequence") # Reseta IDs
        conn.commit()

    # --- CLIENTES (8 Clientes) ---
    clientes_fake = [
        ("Maria Silva", "12345678901", "11988887771", "maria.silva@email.com", "1990-05-15", 35, "Rua das Flores, 10", "Centro", "São Paulo", "01001-000", "Cliente VIP", 500.0),
        ("Ana Oliveira", "23456789012", "11988887772", "ana.oliveira@email.com", "1985-08-20", 36, "Av. Brasil, 500", "Jardins", "São Paulo", "01430-000", "Pagamento em dia", 300.0),
        ("Carla Souza", "34567890123", "11988887773", "carla.souza@email.com", "1992-12-10", 37, "Rua Chile, 12", "Mooca", "São Paulo", "03102-000", "Gosta de cores vivas", 200.0),
        ("Juliana Lima", "45678901234", "11988887774", "juliana.lima@email.com", "1988-03-05", 34, "Rua B, 102", "Lapa", "São Paulo", "05001-000", "Novidades semanais", 100.0),
        ("Patrícia Meira", "56789012345", "11988887775", "patricia.meira@email.com", "1995-07-25", 38, "Travessa Paz, 5", "Itaim", "São Paulo", "04531-000", "Fiel", 400.0),
        ("Renata Costa", "67890123456", "11988887776", "renata.costa@email.com", "1993-01-30", 35, "Rua XV, 20", "Centro", "Curitiba", "80020-000", "Trabalha no centro", 150.0),
        ("Natália Ferreira", "78901234567", "11988887777", "natalia.ferreira@email.com", "1989-11-12", 36, "Rua das Laranjeiras, 44", "Batel", "Curitiba", "80420-000", "Compra presentes", 250.0),
        ("Bianca Santos", "89012345678", "11988887778", "bianca.santos@email.com", "1991-09-02", 37, "Av. Paulista, 1000", "Bela Vista", "São Paulo", "01310-000", "Sapatos exclusivos", 350.0),
    ]

    for c in clientes_fake:
        database.cadastrar_cliente(c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11])

    # --- PRODUTOS (15 Produtos - Adicionados mais 5 para fechar o pedido) ---
    # Ajustado para a assinatura: (sku, tipo, produto, cor, tamanho, precocusto, precovenda, quantidade, categoria, material, fornecedor, foto)
    produtos_fake = [
        ("SAP-001", "Calçados", "Sapatilha Verniz", "Preta", 35, 40.0, 89.90, 18, "Casual", "Sintético", "Fábrica A", "img01.jpg"),
        ("SAP-002", "Calçados", "Sapatilha Matelassê", "Bege", 36, 45.0, 95.00, 20, "Clássico", "Napa", "Fábrica B", "img02.jpg"),
        ("MUL-001", "Calçados", "Mule Bico Fino", "Caramelo", 37, 50.0, 110.00, 12, "Mule", "Couro", "Fábrica A", "img03.jpg"),
        ("SCP-001", "Calçados", "Scarpin Salto Baixo", "Nude", 38, 60.0, 150.00, 10, "Festa", "Verniz", "Fábrica B", "img05.jpg"),
        ("RAS-001", "Calçados", "Rasteira Pedraria", "Dourada", 35, 35.0, 75.00, 16, "Verão", "Sintético", "Fábrica D", "img08.jpg"),
        ("TEN-001", "Calçados", "Tênis Casual", "Branco", 38, 55.0, 129.90, 11, "Esportivo", "Couro", "Fábrica F", "img10.jpg"),
        ("SNE-001", "Calçados", "Tênis Esportivo", "Cinza", 39, 48.0, 139.90, 14, "Esportivo", "Malha", "Fábrica G", "img11.jpg"),
        ("MOC-001", "Calçados", "Mocassim Luxo", "Marrom", 37, 42.0, 129.00, 8, "Casual", "Couro", "Fábrica C", "img12.jpg"),
        ("BNK-001", "Calçados", "Bota Cano Curto", "Preto", 38, 70.0, 179.90, 9, "Inverno", "Couro", "Fábrica E", "img13.jpg"),
        ("ESP-001", "Calçados", "Espadrille Rafia", "Natural", 36, 38.0, 99.90, 7, "Verão", "Rafia", "Fábrica H", "img14.jpg"),
        # +5 variações para completar 15
        ("SAP-003", "Calçados", "Sapatilha Soft", "Azul", 34, 40.0, 85.00, 5, "Casual", "Tecido", "Fábrica A", ""),
        ("RAS-002", "Calçados", "Chinelo Slim", "Rosa", 36, 20.0, 45.00, 25, "Verão", "Borracha", "Fábrica D", ""),
        ("SCP-002", "Calçados", "Scarpin Lux", "Vermelho", 37, 80.0, 199.00, 4, "Festa", "Nobuck", "Fábrica B", ""),
        ("TEN-002", "Calçados", "Tênis Plataforma", "Branco", 35, 65.0, 159.00, 6, "Casual", "Lona", "Fábrica F", ""),
        ("MOC-002", "Calçados", "Mocassim Drive", "Azul Marinho", 40, 55.0, 115.00, 10, "Casual", "Couro", "Fábrica C", ""),
    ]

    for p in produtos_fake:
        database.cadastrar_produto(*p)

    # --- DESPESAS (5 Despesas com Parcelamento/Trimestral) ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    # Assinatura: (fornecedor, descricao, categoria, valor, recorrencia, vencimento, forma_pagamento, status, parcelas, ...)
    despesas_fake = [
        ("Imobiliária", "Aluguel Loja", "Infraestrutura", 3000.0, "Mensal", hoje, "PIX", "Pendente", 1),
        ("Coelba", "Energia", "Utilidades", 450.0, "Mensal", hoje, "Boleto", "Pendente", 1),
        ("Vivo", "Internet Fiber", "Comunicação", 150.0, "Mensal", hoje, "Cartão", "Pendente", 1),
        ("Fornecedor Couros", "Compra de Estoque", "Produtos", 1200.0, "Parcelar", hoje, "Boleto", "Pendente", 3), # Trimestral (3x)
        ("Marketing Digital", "Anúncios Meta", "Marketing", 600.0, "Parcelar", hoje, "PIX", "Pendente", 2),
    ]

    for d in despesas_fake:
        database.cadastrar_despesa(*d)

    # --- 5 VENDAS (Variando Crediário e Outras Formas) ---
    with database.conectar() as conn:
        cursor = conn.cursor()
        clientes_ids = [row[0] for row in cursor.execute("SELECT id FROM clientes").fetchall()]
        produtos_pool = [{"id": r[0], "preco": r[1]} for r in cursor.execute("SELECT id, precovenda FROM produtos WHERE quantidade > 0").fetchall()]

    if clientes_ids and produtos_pool:
        print("-> Registrando 5 vendas estratégicas...")
        for i in range(5):
            c_id = clientes_ids[i]
            # Venda 1 e 2 sempre Crediário 3x para testar o financeiro
            if i < 2:
                forma, parc = "Crediário", 3
            else:
                forma, parc = random.choice(["Pix", "Cartão"]), 1
            
            p_sorteado = random.choice(produtos_pool)
            itens = [{"id": p_sorteado["id"], "qtd": 1, "preco": p_sorteado["preco"]}]
            
            database.realizar_venda_segura(c_id, itens, forma, parc, desconto_total=5.0)

    # --- Auditoria de Pagamento (Quitar 1 despesa e 1 parcela de venda) ---
    with database.conectar() as conn:
        cursor = conn.cursor()
        # Quita a primeira despesa
        id_desp = cursor.execute("SELECT id FROM financeiro WHERE tipo='Despesa' LIMIT 1").fetchone()[0]
        database.quitar_titulo_financeiro(id_desp, "PIX")
        
    print("\n✅ Base de Testes Vs4.4 populada com sucesso!")

if __name__ == "__main__":
    popular_banco()