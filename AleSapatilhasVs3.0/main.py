import tkinter as tk
from tkinter import messagebox, ttk
import database 
from datetime import datetime

class SistemaAleSapatilhas:
    def __init__(self, root):
        self.root = root
        self.root.title("Alê Sapatilhas - Gestão Integrada")
        self.root.geometry("1200x750")
        
        # --- PALETA DE CORES ---
        self.bg_fundo = "#F8FAFC"      
        self.bg_card = "#FFFFFF"       
        self.cor_borda = "#E2E8F0"     
        self.cor_texto = "#0F172A"     
        self.cor_lbl = "#64748B"       
        self.cor_destaque = "#3B82F6"  
        self.cor_btn_acao = "#475569"  
        self.cor_btn_sair = "#1E293B"  
        self.cor_hover_btn = "#334155"
        self.cor_btn_menu = "#223247" 

        self.root.configure(bg=self.bg_fundo)
        self.modo_atual = "clientes" 
        
        self.setup_ui()
        self.exibir_clientes()

    def setup_ui(self):
        # --- MENU LATERAL ---
        self.sidebar = tk.Frame(self.root, bg=self.cor_btn_sair, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="ALÊ\nSAPATILHAS", font=("Segoe UI", 16, "bold"), 
                 bg=self.cor_btn_sair, fg="white", pady=20).pack()

        btn_estilo = {
            "font": ("Segoe UI", 10, "bold"), "bg": self.cor_btn_menu, "fg": "white",
            "relief": "flat", "activebackground": self.cor_hover_btn, 
            "activeforeground": "white", "cursor": "hand2", "anchor": "w", "padx": 20
        }

        botoes = [
            ("➕ GERAR VENDA", self.abrir_cadastro_venda),
            ("📑 LISTAR VENDAS", self.exibir_vendas),
            ("💸 LANÇAR DESPESA", self.abrir_cadastro_despesas),
            ("📉 LISTAR DESPESAS", self.exibir_despesas),
            ("👤 NOVO CLIENTE", self.abrir_cadastro_cliente),
            ("👥 LISTAR CLIENTES", self.exibir_clientes),
            ("📦 NOVO PRODUTO", self.abrir_cadastro_produto),
            ("👠 LISTAR PRODUTOS", self.exibir_produtos),
            ("📊 RELATÓRIO DRE", self.exibir_relatorio_dre),
            ("", None), 
            ("🚪 SAIR", self.confirmar_saida)
        ]

        for texto, comando in botoes:
            if texto == "":
                tk.Label(self.sidebar, bg=self.cor_btn_sair, pady=10).pack()
                continue
            
            cor_bg = self.cor_btn_sair if "SAIR" in texto else self.cor_btn_menu
            btn = tk.Button(self.sidebar, text=texto, command=comando, **btn_estilo)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.cor_hover_btn))
            btn.bind("<Leave>", lambda e, b=btn, c=cor_bg: b.config(bg=c))

        # --- ÁREA PRINCIPAL ---
        self.container = tk.Frame(self.root, bg=self.bg_fundo, padx=20, pady=20)
        self.container.pack(side="right", fill="both", expand=True)

        search_frame = tk.Frame(self.container, bg=self.bg_fundo)
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="🔍 BUSCAR", font=("Segoe UI", 12), bg=self.bg_fundo).pack(side="left")
        self.ent_busca = tk.Entry(search_frame, font=("Segoe UI", 11), bg=self.bg_card, relief="flat", 
                                  highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_busca.pack(side="left", padx=10, fill="x", expand=True, ipady=4)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.filtrar_busca())

        self.lbl_titulo = tk.Label(self.container, text="Lista", font=("Segoe UI", 18, "bold"), 
                                   bg=self.bg_fundo, fg=self.cor_texto)
        self.lbl_titulo.pack(anchor="w", pady=(0, 10))

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=self.bg_card, foreground=self.cor_texto, rowheight=30, borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.cor_destaque)])
        
        self.tree_frame = tk.Frame(self.container, bg=self.bg_card)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", lambda e: self.editar_selecionado())

    def preparar_colunas(self, colunas):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = colunas
        for col in colunas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=120)

    def exibir_clientes(self):
        self.modo_atual = "clientes"
        self.lbl_titulo.config(text="👥 Clientes Cadastrados")
        self.preparar_colunas(("id", "nome", "telefone", "bairro", "tamanho", "status"))
        for c in database.listar_clientes():
            # v[0]=id, v[1]=nome, v[2]=tel, v[7]=bairro, v[4]=tamanho, v[11]=status
            self.tree.insert("", "end", values=(c[0], c[1], c[2], c[7], c[4], c[11]))

    def exibir_produtos(self):
        self.modo_atual = "produtos"
        self.lbl_titulo.config(text="👠 Estoque de Produtos")
        self.preparar_colunas(("id", "produto", "cor", "tamanho", "estoque", "preço"))
        for i in database.listar_itens():
            self.tree.insert("", "end", values=(i[0], i[1], i[2], i[3], i[6], f"R$ {i[5]:.2f}"))

    def exibir_vendas(self):
        self.modo_atual = "pedidos"
        self.lbl_titulo.config(text="📑 Controle de Pedidos")
        self.preparar_colunas(("id", "cliente", "total", "pago", "saldo", "status", "data"))
        for v in database.relatorio_vendas_geral():
            # v[0]=id, v[1]=nome, v[2]=total, v[3]=pago, v[6]=saldo, v[7]=status, v[5]=data
            self.tree.insert("", "end", values=(
                v[0], v[1], f"R$ {v[2]:.2f}", f"R$ {v[3]:.2f}", 
                f"R$ {v[6]:.2f}", v[7], v[5]
            ))

    def exibir_despesas(self):
        self.modo_atual = "despesas"
        self.lbl_titulo.config(text="💸 Controle de Despesas")
        self.preparar_colunas(("id", "descrição", "valor", "tipo", "categoria", "data"))
        try:
            for d in database.listar_despesas():
                valor_fmt = f"R$ {d[2]:.2f}".replace(".", ",")
                self.tree.insert("", "end", values=(d[0], d[1], valor_fmt, d[3], d[4], d[5]))
        except Exception as e:
            print(f"Erro ao carregar despesas: {e}")

    def abrir_cadastro_despesas(self):
        from cadastro_despesas import JanelaCadastroDespesas
        janela = JanelaCadastroDespesas(self.root)
        self.root.wait_window(janela) 
        self.exibir_despesas()

    def abrir_cadastro_venda(self):
        item = self.tree.selection()
        if self.modo_atual == "clientes" and item:
            valores = self.tree.item(item, "values")
            from cadastro_vendas import JanelaCadastroVendas
            janela = JanelaCadastroVendas(self.root, cliente_id=valores[0], nome_cliente=valores[1])
            self.root.wait_window(janela)
            self.exibir_vendas()
        else:
            messagebox.showwarning("Atenção", "Selecione um CLIENTE na lista primeiro para iniciar a venda.")
            self.exibir_clientes()

    def exibir_relatorio_dre(self):
        hoje = datetime.now()
        dre = database.relatorio_DRE_resumido(hoje.month, hoje.year)
        texto = (f"📊 DRE - {hoje.month}/{hoje.year}\n{'-'*30}\n"
                 f"Faturamento: R$ {dre['Faturamento Bruto']:.2f}\n"
                 f"Custos: R$ {dre['(-) Custo Produtos']:.2f}\n"
                 f"Despesas: R$ {dre['(-) Despesas Loja']:.2f}\n"
                 f"LUCRO: R$ {dre['LUCRO LÍQUIDO']:.2f}")
        messagebox.showinfo("DRE Mensal", texto)

    def editar_selecionado(self):
        item_id = self.tree.selection()
        if not item_id: return
        id_banco = self.tree.item(item_id, "values")[0]

        if self.modo_atual == "clientes":
            from cadastro_clientes import JanelaCadastroClientes
            dados = next((c for c in database.listar_clientes() if str(c[0]) == str(id_banco)), None)
            if dados: 
                janela = JanelaCadastroClientes(self.root, dados_cliente=dados)
                self.root.wait_window(janela)
                self.exibir_clientes()

        elif self.modo_atual == "produtos":
            from cadastro_produtos import JanelaCadastroProdutos
            dados = next((i for i in database.listar_itens() if str(i[0]) == str(id_banco)), None)
            if dados: 
                janela = JanelaCadastroProdutos(self.root, dados_produto=dados)
                self.root.wait_window(janela)
                self.exibir_produtos()

    def abrir_cadastro_cliente(self):
        from cadastro_clientes import JanelaCadastroClientes
        janela = JanelaCadastroClientes(self.root)
        self.root.wait_window(janela)
        self.exibir_clientes()

    def abrir_cadastro_produto(self):
        from cadastro_produtos import JanelaCadastroProdutos
        janela = JanelaCadastroProdutos(self.root)
        self.root.wait_window(janela)
        self.exibir_produtos()

    def filtrar_busca(self):
        termo = self.ent_busca.get().lower()
        for item in self.tree.get_children():
            valor_coluna = str(self.tree.item(item)['values'][1]).lower()
            if termo in valor_coluna: self.tree.reattach(item, '', 'end')
            else: self.tree.detach(item)

    def confirmar_saida(self):
        if messagebox.askyesno("Sair", "Deseja encerrar o sistema?"):
            self.root.destroy()

if __name__ == "__main__":
    database.criar_tabelas() # Garante a existência do banco
    root = tk.Tk()
    app = SistemaAleSapatilhas(root)
    root.mainloop()