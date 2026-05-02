import database
import random
from datetime import datetime

def popular_banco():
    print("=== Iniciando Povoamento do Banco de Dados Ale Sapatilhas ===")
    
    # 1. Garantir que as tabelas existam
    database.criar_tabelas()

    # --- 20 CLIENTES (Adicionado campo Status no final) ---
    clientes_fake = [
        ("Maria Silva", "11988887771", "1990-05-15", 35, "Rua das Flores", 10, "Centro", "São Paulo", "Perto do Mercado", "Cliente VIP", "Ativo"),
        ("Ana Oliveira", "11988887772", "1985-08-20", 36, "Av. Brasil", 500, "Jardins", "São Paulo", "Prédio Azul", "", "Ativo"),
        ("Carla Souza", "11988887773", "1992-12-10", 37, "Rua Chile", 12, "Mooca", "São Paulo", "", "Gosta de brilho", "Ativo"),
        ("Juliana Lima", "11988887774", "1988-03-05", 34, "Rua B", 102, "Lapa", "São Paulo", "Frente à praça", "", "Ativo"),
        ("Patricia Meira", "11988887775", "1995-07-25", 38, "Travessa Paz", 5, "Itaim", "São Paulo", "", "", "Ativo"),
        ("Fernanda Costa", "11988887776", "1980-01-30", 35, "Rua 7 de Setembro", 45, "Centro", "Osasco", "", "Idosa", "Ativo"),
        ("Beatriz Santos", "11988887777", "1998-11-12", 36, "Av. Paulista", 1500, "Bela Vista", "São Paulo", "Conjunto Nacional", "", "Ativo"),
        ("Sandra Rocha", "11988887778", "1975-06-18", 39, "Rua Augusta", 80, "Cerqueira César", "São Paulo", "", "", "Ativo"),
        ("Renata Alves", "11988887779", "1991-09-09", 37, "Rua da Consolação", 200, "Centro", "São Paulo", "", "", "Ativo"),
        ("Monica Pereira", "11988887780", "1987-04-22", 35, "Rua Vergueiro", 1010, "Vila Mariana", "São Paulo", "", "PCD", "Ativo"),
        ("Lúcia Ferreira", "11988887781", "1960-02-14", 38, "Rua Domingos", 22, "Saúde", "São Paulo", "", "", "Ativo"),
        ("Amanda Nunes", "11988887782", "1993-10-01", 34, "Rua Joaquim", 33, "Cambuci", "São Paulo", "", "", "Ativo"),
        ("Vanessa Guedes", "11988887783", "1989-11-20", 36, "Rua Independência", 44, "Ipiranga", "São Paulo", "Perto do Museu", "", "Ativo"),
        ("Tatiana Mello", "11988887784", "1984-05-05", 37, "Av. Jabaquara", 55, "Jabaquara", "São Paulo", "", "", "Ativo"),
        ("Bruna Vieira", "11988887785", "1996-08-08", 35, "Rua Santa Cruz", 66, "Vila Mariana", "São Paulo", "", "", "Ativo"),
        ("Camila Diniz", "11988887786", "1991-12-25", 36, "Rua Turiassu", 77, "Perdizes", "São Paulo", "", "", "Ativo"),
        ("Debora Silva", "11988887787", "1982-03-15", 38, "Av. Sumaré", 88, "Pompeia", "São Paulo", "", "", "Ativo"),
        ("Erika Ramos", "11988887788", "1990-06-06", 35, "Rua Clélia", 99, "Lapa", "São Paulo", "", "", "Ativo"),
        ("Priscila Kato", "11988887789", "1988-07-07", 34, "Rua Heitor Penteado", 111, "Sumaré", "São Paulo", "", "", "Ativo"),
        ("Leticia Spiller", "11988887790", "1985-02-02", 37, "Av. Angélica", 222, "Higienópolis", "São Paulo", "", "", "Inativo")
    ]

    for c in clientes_fake:
        try:
            database.salvar_cliente(*c)
        except Exception as e:
            print(f"Erro cliente {c[0]}: {e}")

    # --- 20 PRODUTOS (Adicionado campo Status no final) ---
    produtos_fake = [
        ("Sapatilha Verniz Preta", "Preta", 35, 40.0, 89.90, 10, "Casual", "Fabrica A", "Disponível"),
        ("Sapatilha Matelassê Bege", "Bege", 36, 45.0, 95.00, 15, "Clássico", "Fabrica B", "Disponível"),
        ("Mule Bico Fino Caramelo", "Caramelo", 37, 50.0, 110.00, 8, "Mule", "Fabrica A", "Disponível"),
        ("Sapatilha Boneca Vermelha", "Vermelha", 34, 42.0, 85.00, 5, "Casual", "Fabrica C", "Disponível"),
        ("Scarpin Nude Salto Baixo", "Nude", 38, 60.0, 150.00, 12, "Festa", "Fabrica B", "Disponível"),
        ("Sapatilha Glitter Prata", "Prata", 36, 48.0, 99.00, 7, "Festa", "Fabrica C", "Disponível"),
        ("Sapatilha Camurça Azul", "Azul", 37, 38.0, 79.90, 20, "Promoção", "Fabrica A", "Disponível"),
        ("Rasteira Pedraria", "Dourada", 35, 35.0, 75.00, 10, "Verão", "Fabrica D", "Disponível"),
        ("Sapatilha Floral", "Estampada", 36, 40.0, 89.90, 6, "Primavera", "Fabrica D", "Disponível"),
        ("Sapatilha Bico Fino Branca", "Branca", 37, 45.0, 95.00, 4, "Noiva", "Fabrica B", "Disponível"),
        ("Mule Animal Print", "Onça", 38, 55.0, 120.00, 9, "Mule", "Fabrica A", "Disponível"),
        ("Sapatilha Laço Clássico", "Rosa", 35, 40.0, 89.90, 11, "Casual", "Fabrica C", "Disponível"),
        ("Sapatilha Confort Soft", "Cinza", 39, 50.0, 105.00, 14, "Confort", "Fabrica E", "Disponível"),
        ("Sapatilha Jeans", "Azul", 36, 35.0, 70.00, 18, "Casual", "Fabrica E", "Disponível"),
        ("Scarpin Preto Camurça", "Preto", 37, 65.0, 160.00, 5, "Festa", "Fabrica B", "Disponível"),
        ("Sapatilha Verniz Nude", "Nude", 35, 40.0, 89.90, 10, "Casual", "Fabrica A", "Disponível"),
        ("Rasteira Nó Marrom", "Marrom", 38, 30.0, 65.00, 12, "Verão", "Fabrica D", "Disponível"),
        ("Sapatilha Metalizada Ouro", "Ouro", 36, 48.0, 99.90, 7, "Festa", "Fabrica C", "Disponível"),
        ("Sapatilha Alpargata", "Verde", 37, 30.0, 60.00, 15, "Casual", "Fabrica E", "Disponível"),
        ("Mule Soft White", "Branco", 34, 50.0, 115.00, 6, "Mule", "Fabrica A", "Disponível")
    ]

    for p in produtos_fake:
        try:
            database.salvar_item(*p)
        except Exception as e:
            print(f"Erro produto {p[0]}: {e}")

    # --- 5 DESPESAS FIXAS (Para o Relatório DRE) ---
    despesas = [
        ("Aluguel Loja", 1500.00, "Fixo", "Infraestrutura"),
        ("Energia Elétrica", 250.00, "Fixo", "Contas"),
        ("Internet", 100.00, "Fixo", "Contas"),
        ("Marketing Instagram", 300.00, "Adicional", "Publicidade"),
        ("Café e Limpeza", 80.00, "Adicional", "Manutenção")
    ]
    for d in despesas:
        database.registrar_despesa(*d)

    # --- 10 VENDAS ---
    formas_pag = ["Pix", "Cartão Crédito", "Dinheiro", "Cartão Débito"]
    clientes_ids = [c[0] for c in database.listar_clientes()]
    produtos = database.listar_itens() # Pega a lista completa de produtos

    if clientes_ids and produtos:
        for _ in range(10):
            c_id = random.choice(clientes_ids)
            # Seleciona de 1 a 3 produtos por venda
            num_produtos = random.randint(1, 3)
            itens_venda = []
            
            for _ in range(num_produtos):
                p = random.choice(produtos)
                # p[0]=id, p[5]=precovenda
                itens_venda.append((p[0], 1, p[5])) 

            # registrar_venda(cliente_id, lista_produtos, desconto, valor_pago, forma_pagamento, perc_comissao)
            desconto = random.choice([0, 5, 10])
            f_pag = random.choice(formas_pag)
            
            # Calcula valor total para simular pagamento integral
            total = sum(item[1] * item[2] for item in itens_venda) - desconto
            
            database.registrar_venda(c_id, itens_venda, desconto, total, f_pag, 0.05)

    print("=== Banco de Dados Populado com Sucesso para Versão 3.0 ===")

if __name__ == "__main__":
    popular_banco()