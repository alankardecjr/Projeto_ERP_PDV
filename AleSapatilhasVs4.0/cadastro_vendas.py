import tkinter as tk
from tkinter import messagebox, ttk
import database 
import ui_utils
from PIL import Image
import os

class JanelaCadastroVendas(tk.Toplevel):
    def __init__(self, master, cliente_selecionado=None, dados_venda=None):
        super().__init__(master)
        self.dados_venda = dados_venda
        if isinstance(self.dados_venda, tuple):
            self.dados_venda = {
                'id': self.dados_venda[0],
                'cliente': f"Venda #{self.dados_venda[0]}"
            }

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
        self._manter_em_primeiro_plano()
        
        self.cliente_selecionado = cliente_selecionado # (id, nome, tel) ou None
        self.carrinho = [] # [(id, produto, qtd, preco)]

        self.setup_layout()
        self.carregar_produtos()
        
        # Se cliente foi passado, pré-selecionar
        if self.cliente_selecionado:
            self.lbl_info_cliente.config(text=f"✓ {self.cliente_selecionado[1]}", fg="green")
        elif self.dados_venda is not None:
            self.lbl_info_cliente.config(text=f"✓ {self.dados_venda.get('cliente', 'Venda')}", fg="green")
        
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

        # Campos do cliente
        frame_campos_cli = tk.Frame(self.frame_esq, bg=self.bg_fundo)
        frame_campos_cli.pack(fill="x", pady=5)
        
        # Nome
        tk.Label(frame_campos_cli, text="Nome:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        self.ent_nome_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_nome_cli.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # CPF
        tk.Label(frame_campos_cli, text="CPF:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        self.ent_cpf_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_cpf_cli.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Telefone
        tk.Label(frame_campos_cli, text="Telefone:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w")
        self.ent_tel_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_tel_cli.grid(row=2, column=1, sticky="ew", padx=(5, 0))
        
        # Endereço completo
        tk.Label(frame_campos_cli, text="Endereço:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w")
        self.ent_end_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_end_cli.grid(row=3, column=1, sticky="ew", padx=(5, 0))
        
        # Número
        tk.Label(frame_campos_cli, text="Número:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=4, column=0, sticky="w")
        self.ent_num_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_num_cli.grid(row=4, column=1, sticky="ew", padx=(5, 0))
        
        # Bairro
        tk.Label(frame_campos_cli, text="Bairro:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=5, column=0, sticky="w")
        self.ent_bairro_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_bairro_cli.grid(row=5, column=1, sticky="ew", padx=(5, 0))
        
        # Cidade
        tk.Label(frame_campos_cli, text="Cidade:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=6, column=0, sticky="w")
        self.ent_cidade_cli = tk.Entry(frame_campos_cli, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_cidade_cli.grid(row=6, column=1, sticky="ew", padx=(5, 0))
        
        # Status VIP
        tk.Label(frame_campos_cli, text="Status:", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9)).grid(row=7, column=0, sticky="w")
        self.var_status_cli = tk.StringVar(value="Ativo")
        self.cb_status_cli = ttk.Combobox(frame_campos_cli, textvariable=self.var_status_cli, values=["Ativo", "Vip", "Inativo"], state="readonly", font=("Segoe UI", 10))
        self.cb_status_cli.grid(row=7, column=1, sticky="ew", padx=(5, 0))
        
        frame_campos_cli.columnconfigure(1, weight=1)

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
        # Adicionada coluna de Foto para mostrar miniatura
        self.tree = ttk.Treeview(self.frame_esq, columns=("Foto", "ID", "Produto", "Qtd", "Preço", "Subtotal"), show="headings")
        for col, width in [("Foto", 60), ("ID", 40), ("Produto", 150), ("Qtd", 50), ("Preço", 80), ("Subtotal", 80)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
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
            ("❌ CANCELAR", self.cancelar_venda)
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
    def _manter_em_primeiro_plano(self):
        try:
            self.attributes("-topmost", True)
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível manter esta janela em primeiro plano: {e}")
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
            # Preencher campos
            cli = res[0]
            self.ent_nome_cli.delete(0, tk.END)
            self.ent_nome_cli.insert(0, cli[1] or "")
            self.ent_cpf_cli.delete(0, tk.END)
            self.ent_cpf_cli.insert(0, cli[2] or "")
            self.ent_tel_cli.delete(0, tk.END)
            self.ent_tel_cli.insert(0, cli[3] or "")
            endereco_parts = (cli[7] or "").split(", ")
            if len(endereco_parts) > 1:
                self.ent_end_cli.delete(0, tk.END)
                self.ent_end_cli.insert(0, endereco_parts[0])
                self.ent_num_cli.delete(0, tk.END)
                self.ent_num_cli.insert(0, endereco_parts[1] if len(endereco_parts) > 1 else "")
            else:
                self.ent_end_cli.delete(0, tk.END)
                self.ent_end_cli.insert(0, cli[7] or "")
                self.ent_num_cli.delete(0, tk.END)
            self.ent_bairro_cli.delete(0, tk.END)
            self.ent_bairro_cli.insert(0, cli[8] or "")
            self.ent_cidade_cli.delete(0, tk.END)
            self.ent_cidade_cli.insert(0, cli[9] or "")
            self.var_status_cli.set(cli[14] or "Ativo")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado!")

    def adicionar_item(self):
        sel = self.cb_produtos.current()
        if sel < 0: return
        
        p = self.produtos_db[sel] # (id, prod, cor, tam, custo, venda, qtd, cat, mat, forn, status, foto)
        
        if p[6] <= 0:
            messagebox.showwarning("Estoque", "Produto sem estoque disponível.")
            return

        # Verifica se já está no carrinho para somar qtd
        for item in self.carrinho:
            if item[0] == p[0]:
                messagebox.showinfo("PDV", "Item já adicionado. Ajuste a quantidade na tabela (Funcionalidade em breve) ou remova e adicione novamente.")
                return

        subtotal = p[5]
        
        # Carregar miniatura da foto
        foto_miniatura = self.carregar_miniatura_foto(p[12])  # p[12] é o caminho da foto
        
        self.carrinho.append([p[0], p[1], 1, p[5], subtotal, foto_miniatura])
        self.tree.insert("", "end", values=("", p[0], p[1], 1, f"R$ {p[5]:.2f}", f"R$ {subtotal:.2f}"))
        
        # Inserir a imagem na primeira coluna
        item_id = self.tree.get_children()[-1]  # Último item inserido
        if foto_miniatura:
            self.tree.set(item_id, "Foto", "")  # Placeholder para a imagem
            # Armazenar referência da imagem para evitar garbage collection
            if not hasattr(self, 'imagens_carrinho'):
                self.imagens_carrinho = []
            self.imagens_carrinho.append(foto_miniatura)
        
        self.atualizar_totais()

    def carregar_miniatura_foto(self, caminho_foto):
        """Carrega e redimensiona a foto do produto para miniatura"""
        if not caminho_foto or not os.path.exists(caminho_foto):
            return None
        
        try:
            # Carregar imagem e redimensionar para 40x40 pixels
            img = Image.open(caminho_foto)
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            return tk.PhotoImage(img)
        except Exception as e:
            print(f"Erro ao carregar foto {caminho_foto}: {e}")
            return None

    def remover_item(self):
        sel = self.tree.selection()
        if not sel: return
        item_values = self.tree.item(sel)["values"]
        # Remover do carrinho (item[1] é o ID do produto)
        self.carrinho = [i for i in self.carrinho if i[0] != item_values[1]]  # item_values[1] é o ID
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
        # Mostrar lista de produtos disponíveis
        from tkinter import Toplevel, ttk
        janela_estoque = Toplevel(self)
        janela_estoque.title("Estoque de Produtos")
        janela_estoque.configure(bg=self.bg_fundo)
        ui_utils.calcular_dimensoes_janela(janela_estoque, largura_desejada=800, altura_desejada=600)
        
        tk.Label(janela_estoque, text="📦 ESTOQUE DISPONÍVEL", font=("Segoe UI", 14, "bold"), bg=self.bg_fundo, fg=self.cor_texto).pack(pady=10)
        
        tree = ttk.Treeview(janela_estoque, columns=("SKU", "Produto", "Cor", "Tam", "Qtd", "Preço"), show="headings")
        for col, width in [("SKU", 80), ("Produto", 150), ("Cor", 60), ("Tam", 40), ("Qtd", 50), ("Preço", 80)]:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        produtos = database.listar_itens()
        for p in produtos:
            if p[6] > 0:  # quantidade > 0
                tree.insert("", "end", values=(p[1], p[2], p[3], p[4], p[6], f"R$ {p[5]:.2f}"))
        
        btn_fechar = tk.Button(janela_estoque, text="FECHAR", bg=self.cor_btn_sair, fg="white", font=("Segoe UI", 10, "bold"), command=janela_estoque.destroy)
        btn_fechar.pack(pady=10)

    def cancelar_venda(self):
        if messagebox.askyesno("Cancelar Venda", "Tem certeza que deseja cancelar a venda? Todos os dados serão perdidos."):
            self.destroy()

    def atalho_vendas(self):
        messagebox.showinfo("Vendas", "Abrindo resumo de vendas do dia...")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroVendas(root)
    root.mainloop()