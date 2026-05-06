import tkinter as tk
from tkinter import messagebox, ttk
import database 
from datetime import datetime
import ui_utils

class SistemaAleSapatilhas:
    def __init__(self, root):
        self.root = root
        self.root.title("Alê Sapatilhas - Gestão Integrada v4.0")
        
        # --- Aplicar dimensões maximizadas ---
        ui_utils.calcular_dimensoes_janela(self.root, maximizar=True)
           
        # --- Paleta de cores (Padronizada) ---
        paleta = ui_utils.get_paleta()
        self.bg_fundo       = paleta["bg_fundo"]
        self.bg_card        = paleta["bg_card"]
        self.cor_borda      = paleta["cor_borda"]
        self.cor_texto      = paleta["cor_texto"]
        self.cor_lbl        = paleta["cor_lbl"]
        self.cor_destaque   = paleta["cor_destaque"]
        self.cor_btn_menu   = paleta["cor_btn_menu"]
        self.cor_btn_sair   = paleta["cor_btn_sair"]
        self.cor_btn_acao   = paleta["cor_btn_acao"]
        self.cor_hover_btn  = paleta["cor_hover_btn"]

        self.root.configure(bg=self.bg_fundo)
        self.modo_atual = "clientes" 
        
        self.setup_ui()
        self.exibir_clientes() # Inicia visualizando clientes

    def setup_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=self.cor_btn_sair, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="ALÊ\nSAPATILHAS", font=("Segoe UI", 18, "bold"), 
                 bg=self.cor_btn_sair, fg="white", pady=20).pack()

        btn_estilo = {
            "font": ("Segoe UI", 10, "bold"), "bg": self.cor_btn_menu, "fg": "white",
            "relief": "flat", "activebackground": self.cor_hover_btn, 
            "activeforeground": "white", "cursor": "hand2", "anchor": "w", "padx": 20
        }

        botoes = [
            ("➕ LANÇAR VENDA", self.abrir_cadastro_vendas),
            ("📑 LISTAR VENDAS", self.exibir_vendas),
            ("💸 LANÇAR FINANCEIRO", self.abrir_cadastro_despesas), 
            ("📉 FLUXO DE CAIXA", self.exibir_financeiro),
            ("👤 CADASTRAR CLIENTE", self.abrir_cadastro_cliente),
            ("👥 LISTAR CLIENTES", self.exibir_clientes),
            ("📦 CADASTRAR PRODUTO", self.abrir_cadastro_produto),
            ("👠 LISTAR PRODUTOS", self.exibir_produtos),
            ("📊 DASHBOARD", self.exibir_dashboard),
            ("", None), 
            ("🚪 SAIR", self.confirmar_saida)
        ]

        for texto, comando in botoes:
            if texto == "":
                tk.Label(self.sidebar, bg=self.cor_btn_sair, pady=10).pack()
                continue

            # --- Criando botões com estilo e hover ---
            btn = tk.Button(self.sidebar, text=texto, command=comando, **btn_estilo)
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.cor_hover_btn))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.cor_btn_menu))

        # --- Container Principal para exibir conteúdo dinâmico ---
        self.container = tk.Frame(self.root, bg=self.bg_fundo, padx=20, pady=20)
        self.container.pack(side="right", fill="both", expand=True)

        # --- Barra de busca rápida ---
        search_frame = tk.Frame(self.container, bg=self.bg_fundo)
        search_frame.pack(fill="x", pady=(0, 10))
        tk.Label(search_frame, text="🔍 BUSCA RÁPIDA", font=("Segoe UI", 10, "bold"), bg=self.bg_fundo).pack(side="left")
        self.ent_busca = tk.Entry(search_frame, font=("Segoe UI", 10), bg=self.bg_card, relief="flat", 
                                  highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_busca.pack(side="left", padx=10, fill="x", expand=True, ipady=4)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.filtrar_busca())

        self.lbl_titulo = tk.Label(self.container, text="Lista", font=("Segoe UI", 18, "bold"), 
                                   bg=self.bg_fundo, fg=self.cor_texto)
        self.lbl_titulo.pack(anchor="w", pady=(0, 10))

        # --- Tabela (Treeview) ---
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=self.bg_card, foreground=self.cor_texto, rowheight=35, borderwidth=0, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=self.bg_card)
        self.style.map("Treeview", background=[('selected', self.cor_destaque)])
        
        self.tree_frame = tk.Frame(self.container, bg=self.bg_card)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, show="headings", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # --- Bindings de interação ---
        self.tree.bind("<Double-1>", lambda e: self.editar_selecionado())
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)
        
    # --- Função para preparar colunas da Treeview de acordo com o modo atual ---
    def preparar_colunas(self, colunas):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = colunas
        for col in colunas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor="center", width=120)

    # --- Funções de carregamento ---
    def exibir_clientes(self):
        self.modo_atual = "clientes"
        self.lbl_titulo.config(text="👥 CADASTRO DE CLIENTES")
        self.preparar_colunas(("id", "nome", "cpf", "telefone", "limite", "status"))    
        for c in database.exibir_clientes():
            # c[12] é limite_credito, c[14] é status_cliente
            self.tree.insert("", "end", values=(c[0], c[1], c[2], c[3], f"R$ {c[12]:.2f}", c[14]))

    def exibir_produtos(self):
        self.modo_atual = "produtos"
        self.lbl_titulo.config(text="👠 ESTOQUE DE PRODUTOS")
        # Ajustado para bater com a ordem do database.exibir_produtos()
        self.preparar_colunas(("id", "sku", "produto", "cor", "tamanho", "estoque", "preço", "status"))
        for i in database.exibir_produtos():
            # i[7] é quantidade, i[6] é precovenda, i[11] é status_item
            self.tree.insert("", "end", values=(i[0], i[1], i[2], i[3], i[4], i[7], f"R$ {i[6]:.2f}", i[11]))

    def exibir_vendas(self):
        self.modo_atual = "vendas"
        self.lbl_titulo.config(text="📑 HISTÓRICO DE VENDAS")
        self.preparar_colunas(("id", "cliente", "total", "forma", "data", "status"))
        for v in database.relatorio_vendas_geral():
            self.tree.insert("", "end", values=(v[0], v[1], f"R$ {v[2]:.2f}", v[3], v[5], v[7]))

    def exibir_financeiro(self):
        self.modo_atual = "financeiro"
        self.lbl_titulo.config(text="📉 FLUXO DE CAIXA")
        self.preparar_colunas(("id", "tipo", "entidade", "descrição", "valor", "vencimento", "status"))
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tipo, entidade_nome, descricao, valor, data_vencimento, status FROM financeiro ORDER BY data_vencimento DESC")
            for f in cursor.fetchall():
                self.tree.insert("", "end", values=(f[0], f[1], f[2], f[3], f"R$ {f[4]:.2f}", f[5], f[6]))

    def exibir_dashboard(self):
        res = database.dashboard_resumo()
        msg = f"📊 STATUS DA LOJA\n{'-'*30}\n"
        msg += f"Contas a Receber: R$ {res['total_a_receber']:.2f}\n"
        if res['alertas_estoque']:
            msg += f"\n🚨 ALERTAS DE ESTOQUE:\n"
            for item in res['alertas_estoque']: msg += f"- {item[0]}: {item[1]} un.\n"
        else: msg += "\n✅ Estoque em dia!"
        messagebox.showinfo("Dashboard Pro", msg)

    # --- Janelas (Imports Lazy para evitar erros de circularidade) ---
    def abrir_cadastro_vendas(self):
        selection = self.tree.selection()
        if self.modo_atual == "clientes" and selection:
            valores = self.tree.item(selection, "values")
            from cadastro_vendas import JanelaCadastroVendas
            JanelaCadastroVendas(self.root, cliente_id=valores[0], nome_cliente=valores[1])
            self.exibir_vendas()
        else:
            messagebox.showwarning("Atenção", "Selecione um CLIENTE na lista para iniciar a venda.")
            self.exibir_clientes()

    def abrir_cadastro_despesas(self):
        from cadastro_despesas import JanelaCadastroDespesas
        JanelaCadastroDespesas(self.root)
        self.exibir_financeiro()

    def abrir_cadastro_cliente(self):
        from cadastro_clientes import JanelaCadastroClientes
        JanelaCadastroClientes(self.root)
        self.exibir_clientes()

    def abrir_cadastro_produto(self):
        from cadastro_produtos import JanelaCadastroProdutos
        JanelaCadastroProdutos(self.root)
        self.exibir_produtos()

    def editar_selecionado(self):
        item_id = self.tree.selection()
        if not item_id: return
        id_banco = self.tree.item(item_id, "values")[0]

        if self.modo_atual == "clientes":
            from cadastro_clientes import JanelaCadastroClientes
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_banco,))
                dados = cursor.fetchone()
                if dados: 
                    JanelaCadastroClientes(self.root, dados_cliente=dados)
                    self.exibir_clientes()

        elif self.modo_atual == "produtos":
            from cadastro_produtos import JanelaCadastroProdutos
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_banco,))
                dados = cursor.fetchone()
                if dados: 
                    JanelaCadastroProdutos(self.root, dados_produto=dados)
                    self.exibir_produtos()

    # --- Função para mostrar menu de contexto ---
    def mostrar_menu_contexto(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            if self.modo_atual in ["clientes", "produtos"]:
                menu.add_command(label="📝 Editar", command=self.editar_selecionado)
                menu.add_command(label="🚫 Desativar/Excluir", command=self.excluir_logico)
            elif self.modo_atual == "financeiro":
                menu.add_command(label="✅ Quitar Título", command=self.quitar_selecionado)
            menu.post(event.x_root, event.y_root)

    def excluir_logico(self):
        item = self.tree.selection()
        if not item: return
        id_banco = self.tree.item(item, "values")[0]
        
        if messagebox.askyesno("Confirmar", "Deseja realmente desativar este registro?"):
            if self.modo_atual == "clientes":
                database.atualizar_cliente(id_banco, status_cliente='Inativo')
                self.exibir_clientes()
            elif self.modo_atual == "produtos":
                database.atualizar_produto(id_banco, status_item='Indisponível')
                self.exibir_produtos()

    def quitar_selecionado(self):
        item = self.tree.selection()
        if not item: return
        id_banco = self.tree.item(item, "values")[0]
        database.quitar_titulo_financeiro(id_banco, "Dinheiro")
        self.exibir_financeiro()

    def filtrar_busca(self):
        termo = self.ent_busca.get().lower()
        # Primeiro, torna todas as linhas visíveis novamente (reattach)
        for item in self.tree.get_children():
            self.tree.reattach(item, '', 'end')
            
        # Agora oculta (detach) as que não batem com o termo
        if termo != "":
            for item in self.tree.get_children():
                valores = self.tree.item(item)['values']
                if not any(termo in str(v).lower() for v in valores):
                    self.tree.detach(item)

    def confirmar_saida(self):
        if messagebox.askyesno("Sair", "Deseja encerrar o sistema Ale Sapatilhas?"):
            self.root.destroy()

if __name__ == "__main__":
    database.criar_tabelas() 
    root = tk.Tk()
    app = SistemaAleSapatilhas(root)
    root.mainloop()