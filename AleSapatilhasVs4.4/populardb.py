import database
import random
from datetime import datetime

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas Vs4.4 ===")
    database.criar_tabelas()

    # --- Limpa dados antigos para gerar um conjunto de teste controlado ---
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pagamentos")
        cursor.execute("DELETE FROM financeiro")
        cursor.execute("DELETE FROM itens_venda")
        cursor.execute("DELETE FROM vendas")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM clientes")
        conn.commit()

    # --- CLIENTES TESTE ---
    clientes_fake = [
        ("Maria Silva", "12345678901", "11988887771", "maria.silva@email.com", "1990-05-15", 35, "Rua das Flores, 10", "Centro", "São Paulo", "01001-000", "Cliente VIP adora novidades", 500.0),
        ("Ana Oliveira", "23456789012", "11988887772", "ana.oliveira@email.com", "1985-08-20", 36, "Av. Brasil, 500", "Jardins", "São Paulo", "01430-000", "Pagamento sempre em dia", 300.0),
        ("Carla Souza", "34567890123", "11988887773", "carla.souza@email.com", "1992-12-10", 37, "Rua Chile, 12", "Mooca", "São Paulo", "03102-000", "Gosta de cores vivas", 200.0),
        ("Juliana Lima", "45678901234", "11988887774", "juliana.lima@email.com", "1988-03-05", 34, "Rua B, 102", "Lapa", "São Paulo", "05001-000", "Quer novidades toda semana", 100.0),
        ("Patrícia Meira", "56789012345", "11988887775", "patricia.meira@email.com", "1995-07-25", 38, "Travessa Paz, 5", "Itaim", "São Paulo", "04531-000", "Cliente fiel", 400.0),
        ("Renata Costa", "67890123456", "11988887776", "renata.costa@email.com", "1993-01-30", 35, "Rua XV, 20", "Centro", "Curitiba", "80020-000", "Trabalha no centro", 150.0),
        ("Natália Ferreira", "78901234567", "11988887777", "natalia.ferreira@email.com", "1989-11-12", 36, "Rua das Laranjeiras, 44", "Batel", "Curitiba", "80420-000", "Compra presentes para amigas", 250.0),
        ("Bianca Santos", "89012345678", "11988887778", "bianca.santos@email.com", "1991-09-02", 37, "Av. Paulista, 1000", "Bela Vista", "São Paulo", "01310-000", "Adora sapatos exclusivos", 350.0),
    ]

    for cliente in clientes_fake:
        database.cadastrar_cliente(*cliente)

    # --- PRODUTOS ---
    produtos_fake = [
        ("SAP-001", "Sapatilha Verniz", "Preta", 35, 40.0, 89.90, 18, "Casual", "Sintético", "Fábrica A", "images/produto01.jpg"),
        ("SAP-002", "Sapatilha Matelassê", "Bege", 36, 45.0, 95.00, 20, "Clássico", "Napa", "Fábrica B", "images/produto02.jpg"),
        ("MUL-001", "Mule Bico Fino", "Caramelo", 37, 50.0, 110.00, 12, "Mule", "Couro", "Fábrica A", "images/produto03.jpg"),
        ("SCP-001", "Scarpin Salto Baixo", "Nude", 38, 60.0, 150.00, 10, "Festa", "Verniz", "Fábrica B", "images/produto05.jpg"),
        ("RAS-001", "Rasteira Pedraria", "Dourada", 35, 35.0, 75.00, 16, "Verão", "Sintético", "Fábrica D", "images/produto08.jpg"),
        ("TEN-001", "Tênis Casual", "Branco", 38, 55.0, 129.90, 11, "Esportivo", "Couro Sintético", "Fábrica F", "images/produto10.jpg"),
        ("SNE-001", "Tênis Esportivo", "Cinza", 39, 48.0, 139.90, 14, "Esportivo", "Malha", "Fábrica G", "images/produto11.jpg"),
        ("MOC-001", "Mocassim Luxo", "Marrom", 37, 42.0, 129.00, 8, "Casual", "Couro", "Fábrica C", "images/produto12.jpg"),
        ("BNK-001", "Bota Cano Curto", "Preto", 38, 70.0, 179.90, 9, "Inverno", "Couro", "Fábrica E", "images/produto13.jpg"),
        ("ESP-001", "Espadrille Rafia", "Natural", 36, 38.0, 99.90, 7, "Verão", "Rafia", "Fábrica H", "images/produto14.jpg"),
    ]

    for produto in produtos_fake:
        database.cadastrar_produto(*produto)

    # --- DESPESAS ---
    hoje = datetime.now().strftime("%Y-%m-%d")
    despesas_fixas = [
        ("Imobiliária Aliança", "Aluguel", "Infraestrutura", 3200.00, "Fixa Mensal", hoje, "PIX", "Pendente", 1, hoje, None, "Valor Fixo", 0.0, "Valor Fixo", 0.0, 3200.0),
        ("Neoenergia", "Energia Elétrica", "Infraestrutura", 520.00, "Fixa Mensal", hoje, "Débito", "Pendente", 1, hoje, None, "Valor Fixo", 0.0, "Valor Fixo", 0.0, 520.0),
        ("Embasa", "Água", "Infraestrutura", 180.00, "Fixa Mensal", hoje, "Boleto", "Pendente", 1, hoje, None, "Valor Fixo", 0.0, "Valor Fixo", 0.0, 180.0),
        ("Vivo", "Internet/Telefone", "Infraestrutura", 190.00, "Fixa Mensal", hoje, "Cartão", "Pendente", 1, hoje, None, "Valor Fixo", 0.0, "Valor Fixo", 0.0, 190.0),
        ("TotalPass", "Serviços de Mobilidade", "Infraestrutura", 120.00, "Parcelar", hoje, "PIX", "Pendente", 3, hoje, None, "Porcentagem", 5.0, "Valor Fixo", 0.0, 120.0),
    ]

    for despesa in despesas_fixas:
        database.cadastrar_despesa(*despesa)

    # --- 5 VENDAS DE TESTE ---
    formas_pag = ["Cartão", "Dinheiro", "Pix"]

    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes")
        clientes_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id, precovenda, quantidade FROM produtos WHERE quantidade > 0")
        produtos_pool = [{"id": row[0], "preco": row[1], "qtd": row[2]} for row in cursor.fetchall()]

    if clientes_ids and produtos_pool:
        print("-> Registrando 5 vendas de teste...")
        clientes_selecionados = random.sample(clientes_ids, min(5, len(clientes_ids)))
        for cliente_id in clientes_selecionados:
            forma = random.choice(formas_pag)
            parcelas = 1 if forma != "Cartão" else random.randint(1, 3)
            qtd_produtos_venda = random.randint(1, 3)
            produtos_disponiveis = [p for p in produtos_pool if p["qtd"] > 0]
            if not produtos_disponiveis:
                break
            selecao = random.sample(produtos_disponiveis, min(qtd_produtos_venda, len(produtos_disponiveis)))
            itens_venda = [{"id": p["id"], "qtd": 1, "preco": p["preco"]} for p in selecao]
            desconto = random.choice([0.0, 5.0, 10.0])
            sucesso, msg = database.realizar_venda_segura(cliente_id, itens_venda, forma, parcelas, desconto)
            if not sucesso:
                print(f"Erro na venda do cliente {cliente_id}: {msg}")

    # --- QUITAR ALGUMAS DESPESAS ---
    with database.conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM financeiro WHERE tipo = 'Despesa' LIMIT 2")
        despesas_id = [row[0] for row in cursor.fetchall()]
        for desp_id in despesas_id:
            database.quitar_titulo_financeiro(desp_id, "Pix")

    print("\n✅ Banco de Dados Vs4.0 populado e sincronizado com sucesso!")

if __name__ == "__main__":
    popular_banco()
