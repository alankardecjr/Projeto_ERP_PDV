import tkinter as tk
from tkinter import messagebox, ttk
import database 
import ui_utils
from datetime import datetime

class JanelaCadastroVendas(tk.Toplevel):
    def __init__(self, master, cliente_selecionado=None, dados_venda=None):
        super().__init__(master)
        
        # Configurações Iniciais
        paleta = ui_utils.get_paleta()
        self.bg_fundo = paleta["bg_fundo"]
        self.bg_card = paleta["bg_card"]
        self.cor_borda = paleta["cor_borda"]
        self.cor_texto = paleta["cor_texto"]
        self.cor_lbl = paleta["cor_lbl"]
        self.cor_destaque = paleta["cor_destaque"]
        self.cor_btn_menu = paleta["cor_btn_menu"]
        self.cor_btn_sair = paleta["cor_btn_sair"]
        
        self.title("Sistema Alê Sapatilhas - Checkout de Vendas")
        self.configure(bg=self.bg_fundo)
        ui_utils.calcular_dimensoes_janela(self, maximizar=True)
        
        # Variáveis de Controle
        self.cliente_atual = cliente_selecionado # (id, nome, cpf, tel...)
        self.carrinho_itens = []
        self.modo_venda = "Venda Nova" if not dados_venda else "Edição"
        
        self.setup_layout()
        self.configurar_estilos()
        
        # Carregamento Inicial
        if self.cliente_atual:
            self.preencher_dados_cliente(self.cliente_atual)
        self.listar_estoque_completo()
        
        self.grab_set()

    def configurar_estilos(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("PDV.Treeview", background=self.bg_card, foreground=self.cor_texto, rowheight=30)
        self.style.configure("PDV.Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def setup_layout(self):
        # --- SIDEBAR (Esquerda) ---
        self.sidebar = tk.Frame(self, bg=self.cor_btn_sair, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="AÇÕES PDV", font=("Segoe UI", 14, "bold"), 
                 bg=self.cor_btn_sair, fg="white", pady=20).pack()

        botoes = [
            ("👤 Cadastrar Cliente", self.abrir_novo_cliente),
            ("📝 Editar Cliente", self.abrir_edicao_cliente),
            ("👠 Listar Estoque", self.listar_estoque_completo),
            ("❌ Remover Item", self.remover_do_carrinho),
            ("💰 Finalizar Venda", self.finalizar_venda),
            ("⬅ Cancelar", self.destroy)
        ]

        for texto, comando in botoes:
            tk.Button(self.sidebar, text=texto, command=comando, font=("Segoe UI", 10, "bold"),
                      bg=self.cor_btn_menu, fg="white", relief="flat", padx=15, pady=10,
                      activebackground=self.cor_destaque, cursor="hand2", anchor="w").pack(fill="x", pady=1)

        # --- CONTAINER PRINCIPAL (Direita) ---
        self.main_container = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        self.main_container.pack(side="right", fill="both", expand=True)

        # 1. ÁREA DO CLIENTE (Topo)
        self.setup_sessao_cliente()

        # 2. ÁREA DE PRODUTOS E BUSCA (Meio)
        self.setup_sessao_produtos()

        # 3. ÁREA DO CARRINHO E TOTAL (Baixo)
        self.setup_sessao_carrinho()

    def setup_sessao_cliente(self):
        frame_cli = tk.Frame(self.main_container, bg=self.bg_fundo)
        frame_cli.pack(fill="x", pady=(0, 10))

        # Busca Rápida Cliente
        lbl_busca = tk.Label(frame_cli, text="🔍 LOCALIZAR CLIENTE", font=("Segoe UI", 10, "bold"), 
                             bg=self.bg_fundo, fg=self.cor_lbl)
        lbl_busca.pack(anchor="w")
        
        self.ent_busca_cli = tk.Entry(frame_cli, font=("Segoe UI", 11), bg=self.bg_card, relief="flat")
        self.ent_busca_cli.pack(fill="x", pady=5)
        self.ent_busca_cli.bind("<KeyRelease>", lambda e: self.buscar_cliente_db())

        # Treeview Resultados Cliente (3 linhas)
        self.tree_cli = ttk.Treeview(frame_cli, columns=("nome", "cpf", "tel"), show="headings", height=3, style="PDV.Treeview")
        self.tree_cli.heading("nome", text="NOME")
        self.tree_cli.heading("cpf", text="CPF")
        self.tree_cli.heading("tel", text="TELEFONE")
        self.tree_cli.pack(fill="x")
        self.tree_cli.bind("<<TreeviewSelect>>", self.selecionar_cliente_busca)

        # Display Dados Cliente (Alinhado à Esquerda)
        self.lbl_dados_cli = tk.Label(frame_cli, text="Nenhum cliente selecionado", font=("Segoe UI", 10),
                                      bg=self.bg_fundo, fg=self.cor_texto, justify="left", anchor="w")
        self.lbl_dados_cli.pack(fill="x", pady=10)

    def setup_sessao_produtos(self):
        frame_prod = tk.Frame(self.main_container, bg=self.bg_fundo)
        frame_prod.pack(fill="both", expand=True)

        # Barra de Busca Produto + Tamanho
        barra_busca = tk.Frame(frame_prod, bg=self.bg_fundo)
        barra_busca.pack(fill="x")

        tk.Label(barra_busca, text="👠 PRODUTO:", font=("Segoe UI", 9, "bold"), bg=self.bg_fundo).grid(row=0, column=0, sticky="w")
        self.ent_busca_prod = tk.Entry(barra_busca, font=("Segoe UI", 10), width=40)
        self.ent_busca_prod.grid(row=0, column=1, padx=5, pady=5)
        self.ent_busca_prod.bind("<KeyRelease>", lambda e: self.filtrar_produtos())

        tk.Label(barra_busca, text="TAMANHO:", font=("Segoe UI", 9, "bold"), bg=self.bg_fundo).grid(row=0, column=2, padx=(15, 0))
        self.ent_tam_filtro = tk.Entry(barra_busca, font=("Segoe UI", 10), width=5)
        self.ent_tam_filtro.grid(row=0, column=3, padx=5)
        self.ent_tam_filtro.bind("<KeyRelease>", lambda e: self.filtrar_produtos())

        # Treeview Estoque
        cols = ("id", "produto", "cor", "tam", "preco", "estoque", "status")
        self.tree_estoque = ttk.Treeview(frame_prod, columns=cols, show="headings", height=8, style="PDV.Treeview")
        for col in cols:
            self.tree_estoque.heading(col, text=col.upper())
            self.tree_estoque.column(col, width=100, anchor="center")
        self.tree_estoque.pack(fill="both", expand=True, pady=5)
        self.tree_estoque.bind("<Double-1>", self.adicionar_ao_carrinho)

    def setup_sessao_carrinho(self):
        frame_cart = tk.Frame(self.main_container, bg=self.bg_card, padx=10, pady=10, 
                              highlightthickness=1, highlightbackground=self.cor_borda)
        frame_cart.pack(fill="x", pady=10)

        tk.Label(frame_cart, text="🛒 RESUMO DA COMPRA", font=("Segoe UI", 10, "bold"), bg=self.bg_card).pack(anchor="w")

        self.tree_cart = ttk.Treeview(frame_cart, columns=("prod", "cor", "tam", "qtd", "sub"), show="headings", height=5, style="PDV.Treeview")
        self.tree_cart.heading("prod", text="PRODUTO")
        self.tree_cart.heading("cor", text="COR")
        self.tree_cart.heading("tam", text="TAM")
        self.tree_cart.heading("qtd", text="QTD")
        self.tree_cart.heading("sub", text="SUBTOTAL")
        self.tree_cart.pack(fill="x", pady=5)

        # Valor Total
        self.lbl_total = tk.Label(frame_cart, text="TOTAL: R$ 0,00", font=("Segoe UI", 18, "bold"), 
                                  bg=self.bg_card, fg=self.cor_destaque)
        self.lbl_total.pack(anchor="e")

    # --- LÓGICA DE NEGÓCIO ---

    def buscar_cliente_db(self):
        termo = self.ent_busca_cli.get()
        self.tree_cli.delete(*self.tree_cli.get_children())
        if len(termo) > 2:
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, cpf, telefone, endereco_completo FROM clientes WHERE nome LIKE ?", (f"%{termo}%",))
                for row in cursor.fetchall():
                    self.tree_cli.insert("", "end", iid=row[0], values=(row[1], row[2], row[3], row[4]))

    def selecionar_cliente_busca(self, event):
        sel = self.tree_cli.selection()
        if sel:
            id_cli = sel[0]
            valores = self.tree_cli.item(id_cli, "values")
            self.cliente_atual = (id_cli, valores[0], valores[1], valores[2], valores[3])
            self.preencher_dados_cliente(self.cliente_atual)

    def preencher_dados_cliente(self, dados):
        info = f"CLIENTE: {dados[1]}  |  CPF: {dados[2]}  |  TEL: {dados[3]}\nENDEREÇO: {dados[4] if len(dados)>4 else 'N/A'}"
        self.lbl_dados_cli.config(text=info)

    def listar_estoque_completo(self):
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        for p in database.listar_itens():
            # Filtro: id[0], sku[1], prod[2], cor[3], tam[4], custo[5], venda[6], qtd[7], status[11]
            self.tree_estoque.insert("", "end", iid=p[0], values=(p[0], p[2], p[3], p[4], f"R$ {p[6]:.2f}", p[7], p[11]))

    def filtrar_produtos(self):
        termo = self.ent_busca_prod.get().lower()
        tam = self.ent_tam_filtro.get()
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        for p in database.listar_itens():
            match_nome = termo in p[2].lower() or termo in p[3].lower()
            match_tam = tam == "" or str(p[4]) == tam
            if match_nome and match_tam:
                self.tree_estoque.insert("", "end", iid=p[0], values=(p[0], p[2], p[3], p[4], f"R$ {p[6]:.2f}", p[7], p[11]))

    def adicionar_ao_carrinho(self, event):
        sel = self.tree_estoque.selection()
        if not sel: return
        id_prod = sel[0]
        item = self.tree_estoque.item(id_prod, "values")
        
        # Lógica de somar se já existir ou novo item
        preco = float(item[4].replace("R$ ", ""))
        self.carrinho_itens.append({'id': id_prod, 'prod': item[1], 'cor': item[2], 'tam': item[3], 'preco': preco})
        self.atualizar_carrinho_view()

    def remover_do_carrinho(self):
        sel = self.tree_cart.selection()
        if not sel: return
        idx = self.tree_cart.index(sel[0])
        del self.carrinho_itens[idx]
        self.atualizar_carrinho_view()

    def atualizar_carrinho_view(self):
        self.tree_cart.delete(*self.tree_cart.get_children())
        total = 0
        for item in self.carrinho_itens:
            self.tree_cart.insert("", "end", values=(item['prod'], item['cor'], item['tam'], 1, f"R$ {item['preco']:.2f}"))
            total += item['preco']
        self.lbl_total.config(text=f"TOTAL: R$ {total:.2f}")

    def abrir_novo_cliente(self):
        from cadastro_clientes import JanelaCadastroClientes
        # Mock de callback para quando fechar
        def callback():
            self.buscar_cliente_db() # Atualiza busca
        JanelaCadastroClientes(self.master)

    def abrir_edicao_cliente(self):
        if not self.cliente_atual:
            messagebox.showwarning("Aviso", "Selecione um cliente primeiro!")
            return
        from cadastro_clientes import JanelaCadastroClientes
        # Aqui você buscaria os dados completos do ID para passar
        JanelaCadastroClientes(self.master, dados_cliente=self.cliente_atual)

    def finalizar_venda(self):
        if not self.cliente_atual or not self.carrinho_itens:
            messagebox.showerror("Erro", "Cliente e Produtos são obrigatórios!")
            return
        
        from cadastro_pagamento import JanelaPagamento
        total = float(self.lbl_total.cget("text").replace("TOTAL: R$ ", ""))
        JanelaPagamento(self, self.cliente_atual, self.carrinho_itens, total)

if __name__ == "__main__":
    root = tk.Tk()
    JanelaCadastroVendas(root)
    root.mainloop()