import tkinter as tk
from tkinter import messagebox, ttk
import database 
from datetime import datetime
import ui_utils

class SistemaAleSapatilhas:
    def __init__(self, root):
        self.root = root
        self.root.title("Alê Sapatilhas - Gestão Integrada")
        
        # --- Configuração de UI e Cores ---
        ui_utils.calcular_dimensoes_janela(self.root, maximizar=True)
        paleta = ui_utils.get_paleta()
        self.bg_fundo = paleta["bg_fundo"]
        self.bg_card = paleta["bg_card"]
        self.cor_borda = paleta["cor_borda"]
        self.cor_texto = paleta["cor_texto"]
        self.cor_destaque = paleta["cor_destaque"]
        self.cor_btn_menu = paleta["cor_btn_menu"]
        self.cor_btn_sair = paleta["cor_btn_sair"]
        self.cor_hover_btn = paleta["cor_hover_btn"]

        self.root.configure(bg=self.bg_fundo)
        self.modo_atual = "clientes" 
        self.botoes_menu = {} 
        
        self.setup_ui()
        self.exibir_clientes()

    def formatar_data_exibicao(self, data_str):
        if data_str:
            try:
                return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                return data_str
        return ""

    def setup_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=self.cor_btn_sair, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="ALÊ\nSAPATILHAS", font=("Segoe UI", 18, "bold"), 
                 bg=self.cor_btn_sair, fg="white", pady=20).pack()

        btn_estilo = {
            "font": ("Segoe UI", 10, "bold"), "bg": self.cor_btn_menu, "fg": "white",
            "relief": "flat", "cursor": "hand2", "anchor": "w", "padx": 20, "pady": 10
        }

        botoes = [
            ("➕ LANÇAR VENDA", self.abrir_cadastro_vendas, "vendas"),
            ("📑 LISTAR VENDAS", self.exibir_vendas, "vendas"),
            ("💸 LANÇAR DESPESAS", self.abrir_cadastro_despesas, "financeiro"), 
            ("📉 FLUXO DE CAIXA", self.exibir_financeiro, "financeiro"),
            ("👤 CADASTRAR CLIENTE", self.abrir_cadastro_cliente, "clientes"),
            ("👥 LISTAR CLIENTES", self.exibir_clientes, "clientes"),
            ("📦 CADASTRAR PRODUTO", self.abrir_cadastro_produto, "produtos"),
            ("👠 LISTAR PRODUTOS", self.exibir_produtos, "produtos"),
            ("📊 DASHBOARD", self.exibir_dashboard, "dashboard"),
            ("🔄 ATUALIZAR", self.atualizar_lista, None),
            ("", None, None), 
            ("🚪 SAIR", self.confirmar_saida, None)
        ]

        for texto, comando, modo in botoes:
            if texto == "":
                tk.Label(self.sidebar, bg=self.cor_btn_sair, pady=10).pack()
                continue
            btn = tk.Button(self.sidebar, text=texto,
                            command=lambda c=comando, m=modo: self.executar_comando_menu(c, m), **btn_estilo)
            btn.pack(fill="x", pady=2)
            if modo:
                self.botoes_menu.setdefault(modo, []).append(btn)

        # Container Principal
        self.container = tk.Frame(self.root, bg=self.bg_fundo, padx=20, pady=20)
        self.container.pack(side="right", fill="both", expand=True)

        # Barra de busca
        search_frame = tk.Frame(self.container, bg=self.bg_fundo)
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="🔍 BUSCA RÁPIDA", font=("Segoe UI", 10, "bold"), bg=self.bg_fundo).pack(side="left")
        self.ent_busca = tk.Entry(search_frame, font=("Segoe UI", 10), bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_busca.pack(side="left", padx=10, fill="x", expand=True, ipady=4)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.filtrar_busca())

        self.lbl_titulo = tk.Label(self.container, text="Lista", font=("Segoe UI", 18, "bold"), bg=self.bg_fundo, fg=self.cor_texto)
        self.lbl_titulo.pack(anchor="w", pady=(0, 10))

        # Tabela
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=self.bg_card, foreground=self.cor_texto, rowheight=35, font=("Segoe UI", 10))
        self.style.map("Treeview", background=[('selected', self.cor_destaque)])
        
        self.tree_frame = tk.Frame(self.container, bg=self.bg_card)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        # Bindings
        self.tree.bind("<Double-1>", lambda e: self.editar_selecionado())
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        self.tree.bind("<Motion>", self.focus_linha_mouse)
        
        self.atualizar_destaque_menu()

    def executar_comando_menu(self, comando, modo):
        if comando:
            comando()
        if modo:
            self.modo_atual = modo
            self.atualizar_destaque_menu()

    def atualizar_destaque_menu(self):
        for modo, botoes in self.botoes_menu.items():
            for btn in botoes:
                if modo == self.modo_atual:
                    btn.config(bg=self.cor_destaque, fg="white")
                else:
                    btn.config(bg=self.cor_btn_menu, fg="white")

    def focus_linha_mouse(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.focus(item)
            self.tree.selection_set(item)
        
    def preparar_colunas(self, colunas):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = colunas
        for col in colunas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=120)

    # --- Métodos de Exibição ---
    def exibir_clientes(self):
        self.modo_atual = "clientes"
        self.lbl_titulo.config(text="👥 CADASTRO DE CLIENTES")
        self.preparar_colunas(("nome", "cpf", "telefone", "aniversario", "calcado", "limite", "status"))    
        for c in database.exibir_clientes():
            self.tree.insert("", "end", iid=c[0], values=(c[1], c[2], c[3], self.formatar_data_exibicao(c[5]), c[6], f"R$ {c[12]:.2f}", c[14]))

    def exibir_produtos(self):
        self.modo_atual = "produtos"
        self.lbl_titulo.config(text="👠 ESTOQUE DE PRODUTOS")
        self.preparar_colunas(("sku", "produto", "cor", "tamanho", "estoque", "preço", "fornecedor", "status"))
        for i in database.exibir_produtos():
            self.tree.insert("", "end", iid=i[0], values=(i[1], i[2], i[3], i[4], i[7], f"R$ {i[6]:.2f}", i[10], i[11]))

    def exibir_vendas(self):
        self.modo_atual = "vendas"
        self.lbl_titulo.config(text="📑 HISTÓRICO DE VENDAS")
        self.preparar_colunas(("cliente", "total", "forma", "data", "status"))
        for v in database.relatorio_vendas_geral():
            self.tree.insert("", "end", iid=v[0], values=(v[1], f"R$ {v[2]:.2f}", v[3], self.formatar_data_exibicao(v[5]), v[7]))

    def exibir_financeiro(self):
        self.modo_atual = "financeiro"
        self.lbl_titulo.config(text="💸 FLUXO DE CAIXA")
        self.preparar_colunas(("tipo", "entidade", "descrição", "valor", "vencimento", "pagamento", "status"))
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo, entidade_nome, descricao, valor, data_vencimento, data_pagamento, status FROM financeiro ORDER BY data_vencimento ASC")
            for f in cursor.fetchall():
                tag = ("cancelado",) if f[7] == "Cancelado" else ()
                self.tree.insert("", "end", iid=f[0], values=(f[1], f[2], f[3], f"R$ {f[4]:.2f}", self.formatar_data_exibicao(f[5]), self.formatar_data_exibicao(f[6]), f[7]), tags=tag)

    def abrir_cadastro_vendas(self):
        selection = self.tree.selection()
        cliente_selecionado = None
        if self.modo_atual == "clientes" and selection:
            item_id = selection[0]
            valores = self.tree.item(item_id, "values")
            cliente_selecionado = (item_id, valores[0], valores[2])
        
        from cadastro_vendas import JanelaCadastroVendas
        JanelaCadastroVendas(self.root, cliente_selecionado)
        self.exibir_vendas()

    # --- Lógica de Edição Corrigida ---
    def editar_selecionado(self):
        item_id = self.tree.selection()
        if not item_id: return
        id_banco = item_id[0]

        if self.modo_atual == "clientes":
            from cadastro_clientes import JanelaCadastroClientes
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_banco,))
                dados = cursor.fetchone()
                if dados: JanelaCadastroClientes(self.root, dados_cliente=dados); self.exibir_clientes()

        elif self.modo_atual == "produtos":
            from cadastro_produtos import JanelaCadastroProdutos
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_banco,))
                dados = cursor.fetchone()
                if dados: JanelaCadastroProdutos(self.root, dados_produto=dados); self.exibir_produtos()

        elif self.modo_atual == "financeiro":
            self.editar_financeiro_registro()

        elif self.modo_atual == "vendas":
            self.editar_venda()

    def editar_financeiro_registro(self):
        item = self.tree.selection()
        if not item: return
        registro_id = item[0]

        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tipo, venda_id FROM financeiro WHERE id = ?", (registro_id,))
            result = cursor.fetchone()
            if not result: return
            tipo, venda_id = result
            
            if tipo == "Despesa":
                from cadastro_despesas import JanelaCadastroDespesas
                cursor.execute("SELECT * FROM financeiro WHERE id = ?", (registro_id,))
                dados = cursor.fetchone()
                if dados: JanelaCadastroDespesas(self.root, dados_despesa=dados); self.exibir_financeiro()
            
            elif tipo == "Receita":
                if venda_id:
                    self.tree.selection_set(venda_id) # Tenta selecionar a venda
                    self.editar_venda(venda_id)
                else:
                    messagebox.showinfo("Info", "Receita manual não possui edição de venda.")

    def editar_venda(self, override_id=None):
        item = self.tree.selection()
        id_venda = override_id if override_id else (item[0] if item else None)
        if not id_venda: return
        
        from cadastro_vendas import JanelaCadastroVendas
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id, c.id, c.nome, c.telefone, v.valor_total, v.forma_pagamento, v.qtd_parcelas, v.desconto, v.data_venda
                FROM vendas v JOIN clientes c ON v.cliente_id = c.id WHERE v.id = ?
            """, (id_venda,))
            dados = cursor.fetchone()
            if dados:
                dados_venda = {
                    'id': dados[0], 'cliente': f"{dados[2]} - {dados[3]}",
                    'total': dados[4], 'forma': dados[5], 'parcelas': dados[6],
                    'desconto': dados[7], 'data': dados[8]
                }
                JanelaCadastroVendas(self.root, cliente_selecionado=(dados[1], dados[2], dados[3]), dados_venda=dados_venda)
                self.exibir_vendas()

    # --- Outros Métodos ---
    def mostrar_menu_contexto(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Editar Selecionado", command=self.editar_selecionado)
            menu.post(event.x_root, event.y_root)

    def filtrar_busca(self):
        termo = self.ent_busca.get().lower()
        for item in self.tree.get_children():
            self.tree.reattach(item, '', 'end')
        if termo != "":
            for item in self.tree.get_children():
                valores = self.tree.item(item)['values']
                if not any(termo in str(v).lower() for v in valores):
                    self.tree.detach(item)

    def atualizar_lista(self):
        metodos = {"clientes": self.exibir_clientes, "produtos": self.exibir_produtos, "financeiro": self.exibir_financeiro, "vendas": self.exibir_vendas}
        if self.modo_atual in metodos: metodos[self.modo_atual]()

    def exibir_dashboard(self):
        res = database.dashboard_resumo()
        messagebox.showinfo("Dashboard", f"Contas a Receber: R$ {res['total_a_receber']:.2f}")

    def abrir_cadastro_despesas(self):
        from cadastro_despesas import JanelaCadastroDespesas
        JanelaCadastroDespesas(self.root); self.exibir_financeiro()

    def abrir_cadastro_cliente(self):
        from cadastro_clientes import JanelaCadastroClientes
        JanelaCadastroClientes(self.root); self.exibir_clientes()

    def abrir_cadastro_produto(self):
        from cadastro_produtos import JanelaCadastroProdutos
        JanelaCadastroProdutos(self.root); self.exibir_produtos()

    def confirmar_saida(self):
        if messagebox.askyesno("Sair", "Deseja encerrar o sistema?"): self.root.destroy()

if __name__ == "__main__":
    database.criar_tabelas() 
    root = tk.Tk()
    app = SistemaAleSapatilhas(root)
    root.mainloop()

