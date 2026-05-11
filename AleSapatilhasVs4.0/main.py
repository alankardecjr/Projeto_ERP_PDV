import tkinter as tk
from tkinter import messagebox, ttk
import database 
from datetime import datetime
import ui_utils

class SistemaAleSapatilhas:
    def __init__(self, root):
        self.root = root
        self.root.title("Alê Sapatilhas - Gestão Integrada")
        
        # --- Configurações Iniciais ---
        ui_utils.calcular_dimensoes_janela(self.root, maximizar=True)
        paleta = ui_utils.get_paleta()
        
        self.bg_fundo       = paleta["bg_fundo"]
        self.bg_card        = paleta["bg_card"]
        self.cor_borda      = paleta["cor_borda"]
        self.cor_texto      = paleta["cor_texto"]
        self.cor_destaque   = paleta["cor_destaque"]
        self.cor_btn_menu   = paleta["cor_btn_menu"]
        self.cor_btn_sair   = paleta["cor_btn_sair"]
        self.cor_hover_btn  = paleta["cor_hover_btn"]

        self.root.configure(bg=self.bg_fundo)
        self.modo_atual = "clientes" 
        self.botoes_menu = {}

        self.setup_ui()
        self.exibir_clientes() 

    # --- Funções de Estilo e Efeitos (Hover/Focus) ---
    def aplicar_hover(self, botao):
        """Aplica efeito de mudança de cor ao passar o mouse."""
        botao.bind("<Enter>", lambda e: botao.config(bg=self.cor_hover_btn) if self.modo_atual != botao.modo else None)
        botao.bind("<Leave>", lambda e: botao.config(bg=self.cor_btn_menu) if self.modo_atual != botao.modo else None)

    def aplicar_focus_entry(self, entry):
        """Aplica destaque visual quando o campo ganha foco."""
        entry.bind("<FocusIn>", lambda e: entry.config(highlightbackground=self.cor_destaque, highlightthickness=2))
        entry.bind("<FocusOut>", lambda e: entry.config(highlightbackground=self.cor_borda, highlightthickness=1))

    def formatar_data_exibicao(self, data_str):
        if data_str:
            try:
                return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
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
            "font": ("Segoe UI", 9, "bold"), "bg": self.cor_btn_menu, "fg": "white",
            "relief": "flat", "cursor": "hand2", "anchor": "w", "padx": 15, "pady": 8
        }

        menu_itens = [
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

        for texto, comando, modo in menu_itens:
            btn = tk.Button(self.sidebar, text=texto, command=lambda c=comando, m=modo: self.executar_comando_menu(c, m), **btn_estilo)
            btn.modo = modo
            btn.pack(fill="x", pady=1)
            if modo:
                self.aplicar_hover(btn)
                self.botoes_menu.setdefault(modo, []).append(btn)

        # Container Principal
        self.container = tk.Frame(self.root, bg=self.bg_fundo, padx=20, pady=20)
        self.container.pack(side="right", fill="both", expand=True)

        # Barra de Busca com efeito Focus
        search_frame = tk.Frame(self.container, bg=self.bg_fundo)
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="🔍 BUSCA RÁPIDA", font=("Segoe UI", 9, "bold"), bg=self.bg_fundo).pack(side="left")
        
        self.ent_busca = tk.Entry(search_frame, font=("Segoe UI", 11), bg=self.bg_card, relief="flat", 
                                  highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_busca.pack(side="left", padx=10, fill="x", expand=True, ipady=4)
        self.aplicar_focus_entry(self.ent_busca)
        self.ent_busca.bind("<KeyRelease>", lambda e: self.filtrar_busca())

        self.lbl_titulo = tk.Label(self.container, text="Lista", font=("Segoe UI", 16, "bold"), 
                                   bg=self.bg_fundo, fg=self.cor_texto)
        self.lbl_titulo.pack(anchor="w", pady=(0, 10))

        # Tabela (Treeview)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=self.bg_card, foreground=self.cor_texto, 
                             rowheight=35, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=self.bg_card)
        self.style.map("Treeview", background=[('selected', self.cor_destaque)])
        
        self.tree = ttk.Treeview(self.container, show="headings", selectmode="browse")
        self.tree.pack(fill="both", expand=True)

        # Eventos da Tabela
        self.tree.bind("<Double-1>", lambda e: self.editar_selecionado())
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)

    def executar_comando_menu(self, comando, modo):
        if comando: comando()
        if modo:
            self.modo_atual = modo
            self.atualizar_destaque_menu()

    def atualizar_destaque_menu(self):
        for modo, botoes in self.botoes_menu.items():
            for btn in botoes:
                if modo == self.modo_atual:
                    btn.config(bg=self.cor_destaque)
                else:
                    btn.config(bg=self.cor_btn_menu)

    # --- Métodos de Exibição de Dados (Integrados com Database) ---
    def preparar_colunas(self, colunas, larguras=None):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = colunas
        for i, col in enumerate(colunas):
            self.tree.heading(col, text=col.upper())
            width = larguras[i] if larguras else 120
            self.tree.column(col, anchor="center", width=width)

    def exibir_clientes(self):
        self.lbl_titulo.config(text="👥 CLIENTES CADASTRADOS")
        self.preparar_colunas(("id", "nome", "cpf", "telefone", "aniversário", "limite", "status"), (50, 250, 120, 120, 100, 100, 80))
        for c in database.exibir_clientes():
            # Mapeamento: id=0, nome=1, cpf=2, tel=3, niver=5, limite=12, status=14
            self.tree.insert("", "end", values=(c[0], c[1], c[2], c[3], self.formatar_data_exibicao(c[5]), f"R$ {c[12]:.2f}", c[14]))

    def exibir_produtos(self):
        self.lbl_titulo.config(text="👠 ESTOQUE DISPONÍVEL")
        self.preparar_colunas(("id", "sku", "produto", "cor", "tam", "qtd", "preço", "status"), (50, 100, 200, 100, 50, 60, 100, 100))
        for p in database.exibir_produtos():
            # Mapeamento: id=0, sku=1, produto=2, cor=3, tam=4, qtd=7, preco=6, status=11
            self.tree.insert("", "end", values=(p[0], p[1], p[2], p[3], p[4], p[7], f"R$ {p[6]:.2f}", p[11]))

    def exibir_vendas(self):
        self.lbl_titulo.config(text="📑 HISTÓRICO DE VENDAS")
        self.preparar_colunas(("id", "cliente", "total", "pagamento", "data", "vendedor", "status"), (50, 200, 100, 120, 120, 100, 100))
        for v in database.relatorio_vendas_geral():
            self.tree.insert("", "end", values=(v[0], v[1], f"R$ {v[2]:.2f}", v[3], self.formatar_data_exibicao(v[5]), v[6], v[7]))

    def exibir_financeiro(self):
        self.lbl_titulo.config(text="💸 FLUXO FINANCEIRO")
        self.preparar_colunas(("tipo", "entidade", "descrição", "valor", "vencimento", "status"), (100, 180, 200, 100, 100, 100))
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tipo, entidade_nome, descricao, valor, data_vencimento, status FROM financeiro ORDER BY data_vencimento DESC")
            for f in cursor.fetchall():
                cor = "red" if f[0] == "Despesa" else "green"
                self.tree.insert("", "end", values=(f[0], f[1], f[2], f"R$ {f[4]:.2f}", self.formatar_data_exibicao(f[5]), f[6]))

    def filtrar_busca(self):
        termo = self.ent_busca.get().lower()
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            if any(termo in str(v).lower() for v in valores):
                # Mantém visível (reattach não é necessário se não der detach, 
                # mas para busca dinâmica é melhor reconstruir a visão)
                pass
            else:
                self.tree.detach(item)
        if termo == "": self.atualizar_lista()

    def atualizar_lista(self):
        metodos = {
            "clientes": self.exibir_clientes,
            "produtos": self.exibir_produtos,
            "vendas": self.exibir_vendas,
            "financeiro": self.exibir_financeiro
        }
        if self.modo_atual in metodos: metodos[self.modo_atual]()

    # --- Chamadas de Janelas Externas ---
    def abrir_cadastro_vendas(self):
        from cadastro_vendas import JanelaCadastroVendas
        JanelaCadastroVendas(self.root)
        self.exibir_vendas()

    def abrir_cadastro_cliente(self):
        from cadastro_clientes import JanelaCadastroClientes
        JanelaCadastroClientes(self.root)
        self.exibir_clientes()

    def exibir_dashboard(self):
        res = database.dashboard_resumo()
        msg = f"Resumo Financeiro: R$ {res['total_a_receber']:.2f}\nAtenção ao estoque!"
        messagebox.showinfo("Dashboard", msg)

    def mostrar_menu_contexto(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✏️ Editar", command=self.editar_selecionado)
            menu.add_command(label="🗑️ Excluir (Desativar)", command=self.excluir_logico)
            menu.post(event.x_root, event.y_root)

    def confirmar_saida(self):
        if messagebox.askyesno("Sair", "Encerrar o sistema?"): self.root.destroy()

    def editar_selecionado(self):
        # Lógica para identificar qual janela abrir baseado no modo_atual e ID
        pass

    def excluir_logico(self):
        pass

if __name__ == "__main__":
    database.criar_tabelas() 
    root = tk.Tk()
    app = SistemaAleSapatilhas(root)
    root.mainloop()