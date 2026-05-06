import tkinter as tk
from tkinter import messagebox, ttk
import database 
import ui_utils

class JanelaCadastroVendas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        # --- Importar paleta de cores ---
        paleta = ui_utils.get_paleta()
        self.bg_fundo = paleta["bg_fundo"]
        self.bg_card = paleta["bg_card"]
        self.cor_borda = paleta["cor_borda"]
        self.cor_texto = paleta["cor_texto"]
        self.cor_lbl = paleta["cor_lbl"]
        self.cor_btn_1 = paleta["cor_btn_menu"]   
        self.cor_btn_2 = paleta["cor_btn_acao"]   
        self.cor_btn_sair = paleta["cor_btn_sair"]
        self.cor_hover_field = paleta["cor_hover_field"]
        self.cor_hover_btn = paleta["cor_hover_btn"]
        self.cor_destaque = paleta["cor_destaque"]
        self.cor_btn_pdv = paleta["cor_btn_acao"]
        self.cor_btn_acoes = paleta["cor_btn_acao"]

        self.title("Alê Sapatilhas - Painel de Venda")
        self.configure(bg=self.bg_fundo)
        
        # --- Aplicar dimensões ---
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=1200, altura_desejada=750)
        
        self.cliente_selecionado = None # (id, nome, tel)
        self.carrinho = [] # [(id, produto, qtd, preco)]

        self.setup_layout()
        self.carregar_produtos()
        self.grab_set()

    def setup_layout(self):
        # Frame Esquerdo: Busca e Itens
        self.frame_esq = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=20)
        self.frame_esq.pack(side="left", fill="both", expand=True)

        # --- SEÇÃO CLIENTE ---
        lbl_cli_head = tk.Label(self.frame_esq, text="👤 CLIENTE", font=("Segoe UI", 10, "bold"), bg=self.bg_fundo, fg=self.cor_lbl)
        lbl_cli_head.pack(anchor="w")
        
        frame_cli = tk.Frame(self.frame_esq, bg=self.bg_fundo)
        frame_cli.pack(fill="x", pady=5)
        
        self.ent_busca_cliente = tk.Entry(frame_cli, font=("Segoe UI", 11), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_busca_cliente.pack(side="left", fill="x", expand=True, ipady=4)
        self.ent_busca_cliente.placeholder = "Digite o nome e pressione Enter..."
        
        btn_buscar_cli = tk.Button(frame_cli, text="BUSCAR", bg=self.cor_btn_acoes, fg="white", font=("Segoe UI", 8, "bold"), 
                                   relief="flat", padx=10, command=self.buscar_cliente)
        btn_buscar_cli.pack(side="left", padx=5)

        self.lbl_info_cliente = tk.Label(self.frame_esq, text="Nenhum cliente selecionado", font=("Segoe UI", 9, "italic"), bg=self.bg_fundo, fg="red")
        self.lbl_info_cliente.pack(anchor="w")

        # --- SEÇÃO PRODUTO ---
        tk.Label(self.frame_esq, text="👠 PRODUTO", font=("Segoe UI", 10, "bold"), bg=self.bg_fundo, fg=self.cor_lbl).pack(anchor="w", pady=(20, 5))
        
        self.cb_produtos = ttk.Combobox(self.frame_esq, font=("Segoe UI", 11), state="readonly")
        self.cb_produtos.pack(fill="x", ipady=4)
        
        btn_add = tk.Button(self.frame_esq, text="ADICIONAR AO CARRINHO (F2)", bg=self.cor_destaque, fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", command=self.adicionar_item)
        btn_add.pack(fill="x", pady=10, ipady=8)

        # --- TABELA CARRINHO ---
        self.tree = ttk.Treeview(self.frame_esq, columns=("ID", "Produto", "Qtd", "Preço", "Subtotal"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        self.tree.column("Produto", width=200)
        self.tree.pack(fill="both", expand=True)
        
        btn_remover = tk.Button(self.frame_esq, text="REMOVER ITEM SELECIONADO", bg="#ef4444", fg="white", font=("Segoe UI", 8), relief="flat", command=self.remover_item)
        btn_remover.pack(anchor="e", pady=5)

        # Frame Direito: Resumo e Atalhos
        self.frame_dir = tk.Frame(self, bg=self.bg_card, width=300, padx=20, pady=20, highlightthickness=1, highlightbackground=self.cor_borda)
        self.frame_dir.pack(side="right", fill="y")
        self.frame_dir.pack_propagate(False)

        # --- ATALHOS ---
        tk.Label(self.frame_dir, text="🛠️ ATALHOS RÁPIDOS", font=("Segoe UI", 10, "bold"), bg=self.bg_card).pack(pady=(0, 10))
        
        botoes_atalho = [
            ("👤 EDITAR CLIENTE", self.atalho_cliente),
            ("👠 VER ESTOQUE", self.atalho_estoque),
            ("📑 VENDAS DO DIA", self.atalho_vendas)
        ]
        
        for txt, cmd in botoes_atalho:
            btn = tk.Button(self.frame_dir, text=txt, bg=self.bg_fundo, fg=self.cor_texto, font=("Segoe UI", 9), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, command=cmd)
            btn.pack(fill="x", pady=3, ipady=5)

        # --- TOTAIS ---
        self.spacer = tk.Label(self.frame_dir, bg=self.bg_card).pack(expand=True)
        
        self.lbl_total_itens = tk.Label(self.frame_dir, text="ITENS: 0", font=("Segoe UI", 12), bg=self.bg_card, fg=self.cor_lbl)
        self.lbl_total_itens.pack()
        
        self.lbl_valor_total = tk.Label(self.frame_dir, text="R$ 0,00", font=("Segoe UI", 24, "bold"), bg=self.bg_card, fg=self.cor_destaque)
        self.lbl_valor_total.pack(pady=10)

        self.btn_pagamento = tk.Button(self.frame_dir, text="PAGAMENTO (F5)", bg=self.cor_btn_pdv, fg="white", font=("Segoe UI", 12, "bold"), relief="flat", command=self.abrir_pagamento)
        self.btn_pagamento.pack(fill="x", ipady=15)

    # --- LÓGICA DO PDV ---

    def carregar_produtos(self):
        self.produtos_db = database.listar_itens()
        # Formato: "ID - Produto (Cor) - Tam"
        self.cb_produtos["values"] = [f"{p[0]} - {p[1]} ({p[2]}) - T:{p[3]} | R$ {p[5]:.2f}" for p in self.produtos_db]

    def buscar_cliente(self):
        termo = self.ent_busca_cliente.get().strip()
        if not termo: return
        
        res = database.buscar_cliente_nome(termo) # Função que criamos no database.py
        if res:
            self.cliente_selecionado = res[0] # Pega o primeiro encontrado
            self.lbl_info_cliente.config(text=f"✓ {self.cliente_selecionado[1]}", fg="green")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado!")

    def adicionar_item(self):
        sel = self.cb_produtos.current()
        if sel < 0: return
        
        p = self.produtos_db[sel] # (id, prod, cor, tam, custo, venda, qtd...)
        
        # Verifica se já está no carrinho para somar qtd
        for item in self.carrinho:
            if item[0] == p[0]:
                messagebox.showinfo("PDV", "Item já adicionado. Ajuste a quantidade na tabela (Funcionalidade em breve) ou remova e adicione novamente.")
                return

        subtotal = p[5]
        self.carrinho.append([p[0], p[1], 1, p[5], subtotal])
        self.tree.insert("", "end", values=(p[0], p[1], 1, f"R$ {p[5]:.2f}", f"R$ {subtotal:.2f}"))
        self.atualizar_totais()

    def remover_item(self):
        sel = self.tree.selection()
        if not sel: return
        item_values = self.tree.item(sel)["values"]
        self.carrinho = [i for i in self.carrinho if i[0] != item_values[0]]
        self.tree.delete(sel)
        self.atualizar_totais()

    def atualizar_totais(self):
        total_venda = sum(item[4] for item in self.carrinho)
        self.lbl_total_itens.config(text=f"ITENS: {len(self.carrinho)}")
        self.lbl_valor_total.config(text=f"R$ {total_venda:.2f}")

    def abrir_pagamento(self):
        if not self.cliente_selecionado:
            messagebox.showwarning("PDV", "Selecione um cliente antes de prosseguir.")
            return
        if not self.carrinho:
            messagebox.showwarning("PDV", "Carrinho vazio!")
            return
        
        total = sum(item[4] for item in self.carrinho)
        # Chama a classe de pagamento (Você deve criar a JanelaPagamento similar a esta)
        from cadastro_pagamento import JanelaPagamento
        JanelaPagamento(self, self.cliente_selecionado, self.carrinho, total)

    # --- ATALHOS ---
    def atalho_cliente(self):
        if self.cliente_selecionado:
            from cadastro_clientes import JanelaCadastroClientes
            JanelaCadastroClientes(self, dados_cliente=self.cliente_selecionado)
        else: messagebox.showinfo("Dica", "Busque um cliente primeiro para editar.")

    def atalho_estoque(self):
        messagebox.showinfo("Estoque", "Abrindo consulta rápida de estoque...")

    def atalho_vendas(self):
        messagebox.showinfo("Vendas", "Abrindo resumo de vendas do dia...")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroVendas(root)
    root.mainloop()