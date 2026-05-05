import tkinter as tk
from tkinter import messagebox, ttk
import database 

class JanelaCadastroProdutos(tk.Toplevel):
    def __init__(self, master, dados_produto=None):
        super().__init__(master)
        
        # --- Paleta de cores (Padronizada) ---
        self.bg_fundo       = "#F1F5F9"
        self.bg_card        = "#FFFFFF"
        self.cor_borda      = "#8BA2BD"
        self.cor_texto      = "#0B1933"
        self.cor_lbl        = "#020C18"
        self.cor_destaque   = "#6366F1" 
        self.cor_btn_menu   = "#1E293B"
        self.cor_btn_sair   = "#25324E"
        self.cor_btn_acao   = "#425074" 
        self.cor_hover_btn  = "#6F7CA0" 
        self.cor_hover_field = "#484AD6" 

       # --- Configurações da janela ---
        self.title("Alê Sapatilhas - Gestão de Estoque")
        self.geometry("600x850")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)

        self.root.configure(bg=self.bg_fundo)
        self.root.resizable(False, False)

        self.produto_id = dados_produto[0] if dados_produto else None
        
        self.list_categorias = ["Sapatilhas", "Rasteiras", "Salto Fino", "Salto Block", "Mules", "Tênis", "Botas", "Biquinis", "Roupas"]     
        self.list_materiais = ["Couro", "Camurça", "Nobuck", "PU", "Verniz", "Algodão", "Poliamida", "Suplex"]      
        self.list_tamanhos = [str(i) for i in range(33, 41)] + ["G", "GG", "M", "P", "U"]        
        self.list_cores = ["Amarelo", "Azul", "Branco", "Caramelo", "Massala", "Nude", "Off", "Preto", "Rosa", "Verde", "Vermelho"]
        self.list_status = ["Disponível", "Indisponível", "Esgotado", "Promocional"]

        self.setup_styles()
        self.criar_widgets()
    
        if dados_produto:
            self.preencher_dados(dados_produto)
     
        self.grab_set()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.bg_card, background=self.bg_card, 
                        arrowcolor=self.cor_btn_acao, bordercolor=self.cor_borda)
        style.configure("Busca.Treeview", background="#F8FAFC", rowheight=22, font=("Segoe UI", 9))

    def criar_widgets(self):
        # --- Usando um frame centralizado para garantir que os widgets não fujam ---
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Função para aplicar estilo de foco nos campos ---
        def aplicar_estilo_foco(ent):
            def on_enter(e):
                if self.focus_get() != ent: ent.config(highlightbackground=self.cor_hover_field)
            def on_leave(e):
                if self.focus_get() != ent: ent.config(highlightbackground=self.cor_borda)
            def on_focus_in(e): ent.config(highlightbackground=self.cor_destaque, highlightthickness=2)
            def on_focus_out(e): ent.config(highlightbackground=self.cor_borda, highlightthickness=1)
            ent.bind("<Enter>", on_enter)
            ent.bind("<Leave>", on_leave)
            ent.bind("<FocusIn>", on_focus_in)
            ent.bind("<FocusOut>", on_focus_out)

        # --- Função para criar campos de entrada com rótulos ---
        def criar_campo(parent, texto, row, col=0, colspan=2):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(3, 0))
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                           relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=3, padx=(0, 5) if colspan==1 else 0)
            aplicar_estilo_foco(ent)
            return ent
        # --- Função para criar comboboxes ---
        def criar_combo(parent, texto, lista, row, col, span=1):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(3, 0))
            combo = ttk.Combobox(parent, values=lista, font=("Segoe UI", 10), state="readonly")
            combo.set(lista[0])
            combo.grid(row=row+1, column=col, columnspan=span, sticky="ew", padx=(0, 5) if col==0 else 0)
            return combo

        # --- Título e busca rápida ---
        tk.Label(main_frame, text="Ficha Cadastral do Produto", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(main_frame, text="🔍 BUSCA RÁPIDA", bg=self.bg_fundo, 
                 fg=self.cor_destaque, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        self.ent_busca_interna = tk.Entry(main_frame, font=("Segoe UI", 10), bg=self.bg_card, relief="flat",
                                          highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_busca_interna.grid(row=2, column=0, columnspan=2, sticky="ew", ipady=3)
        self.ent_busca_interna.bind("<KeyRelease>", self.filtrar_busca_interna)
        aplicar_estilo_foco(self.ent_busca_interna)

        self.tree_busca = ttk.Treeview(main_frame, columns=("id", "prod", "forn"), show="headings", height=3, style="Busca.Treeview")
        self.tree_busca.heading("id", text="ID")
        self.tree_busca.heading("prod", text="MODELO")
        self.tree_busca.heading("forn", text="FORNECEDOR")
        self.tree_busca.column("id", width=40, anchor="center")
        self.tree_busca.grid(row=3, column=0, columnspan=2, sticky="ew", pady=2)
        self.tree_busca.bind("<<TreeviewSelect>>", self.selecionar_da_busca)

        tk.Frame(main_frame, height=1, bg=self.cor_borda).grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # --- Campos de entrada - usando função para evitar repetição ---
        self.ent_sku     = criar_campo(main_frame, "CÓDIGO DO PRODUTO*", 5)
        self.ent_produto = criar_campo(main_frame, "DESCRIÇÃO DO MODELO*", 7)
        self.cb_cat      = criar_combo(main_frame, "CATEGORIA*", self.list_categorias, 9, 0)
        self.cb_mat      = criar_combo(main_frame, "MATERIAL", self.list_materiais, 9, 1)

        self.ent_custo = criar_campo(main_frame, "PREÇO DE CUSTO (R$)*", 11, col=0, colspan=1)
        self.ent_custo.bind("<KeyRelease>", self.calcular_markup)
        
        tk.Label(main_frame, text="PREÇO DE VENDA (R$)*", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=11, column=1, sticky="w", pady=(3, 0))
        self.ent_venda = tk.Entry(main_frame, font=("Segoe UI", 10, "bold"), bg="#E2E8F0", fg=self.cor_destaque, 
                                  relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_venda.grid(row=12, column=1, sticky="ew", ipady=3)

        self.ent_forn = criar_campo(main_frame, "FORNECEDOR*", 13)

        # --- Grade de estoque ---
        tk.Label(main_frame, text="GRADE DE ESTOQUE", bg=self.bg_fundo, fg=self.cor_texto, 
                 font=("Segoe UI", 9, "bold")).grid(row=15, column=0, sticky="w", pady=(10, 2))
        
        frame_grade = tk.LabelFrame(main_frame, bg=self.bg_card, relief="groove", borderwidth=1, padx=10, pady=10)
        frame_grade.grid(row=16, column=0, columnspan=2, sticky="ew")
        frame_grade.columnconfigure(0, weight=1)

        self.cb_cor = criar_combo(frame_grade, "COR*", self.list_cores, 0, 0, 2)
        self.cb_tam = criar_combo(frame_grade, "TAMANHO*", self.list_tamanhos, 2, 0, 2)
        self.ent_qtd = criar_campo(frame_grade, "QUANTIDADE*", 4, col=0, colspan=1)
        
        # --- Status do item (OptionMenu/Status) ---
        tk.Label(frame_grade, text="STATUS DO ITEM*", bg=self.bg_card, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=4, column=1, sticky="w", pady=(3, 0))
        self.var_status = tk.StringVar(value="Disponível")
        self.opt_status = tk.OptionMenu(frame_grade, self.var_status, *self.list_status)
        self.opt_status.config(bg=self.bg_fundo, fg=self.cor_texto, relief="flat", highlightthickness=1, 
                                highlightbackground=self.cor_borda, font=("Segoe UI", 9), cursor="hand2")
        self.opt_status.grid(row=5, column=1, sticky="ew", pady=(1, 0))

        # --- Botões ---
        texto_botao = "ATUALIZAR PRODUTO" if self.produto_id else "SALVAR PRODUTO"
        cor_base_acao = self.cor_hover_field if self.produto_id else self.cor_btn_acao

        self.btn_salvar = tk.Button(main_frame, text=texto_botao, bg=cor_base_acao, fg="white", 
                                    font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                    command=self.validar_e_salvar)
        self.btn_salvar.grid(row=17, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=6)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", 
                                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                      command=self.destroy)
        self.btn_cancelar.grid(row=18, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=6)

        # --- Hovers ---
        self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=cor_base_acao))
        self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        self.atualizar_tree_busca()

    # --- Cálculo automático do preço de venda com base no custo ---
    def calcular_markup(self, event=None):
        try:
            custo = self.ent_custo.get().replace(",", ".")
            if custo:
                venda = float(custo) * 2.5
                self.ent_venda.delete(0, tk.END)
                self.ent_venda.insert(0, f"{venda:.2f}")
        except ValueError:
            self.ent_venda.delete(0, tk.END)

    # --- Atualiza a treeview da busca rápida com os produtos do banco ---
    def atualizar_tree_busca(self):
        self.tree_busca.delete(*self.tree_busca.get_children())
        for p in database.exibir_produtos():
            self.tree_busca.insert("", "end", values=(p[0], p[2], p[10]))

    def filtrar_busca_interna(self, event=None):
        termo = self.ent_busca_interna.get().lower()
        self.tree_busca.delete(*self.tree_busca.get_children())
        for p in database.exibir_produtos():
            if termo in str(p[2]).lower() or termo in str(p[10]).lower():
                self.tree_busca.insert("", "end", values=(p[0], p[2], p[10]))

    def selecionar_da_busca(self, event):
        selecao = self.tree_busca.selection()
        if not selecao: return
        id_prod = self.tree_busca.item(selecao)["values"][0]
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_prod,))
            dados = cursor.fetchone()
            if dados: self.preencher_dados(dados
                                           )
    # --- Lógica de validar campos e salvar no banco ---
    def validar_e_salvar(self):
        try:
            d = {
                "sku": self.ent_sku.get().strip(),
                "produto": self.ent_produto.get().strip(),
                "cor": self.cb_cor.get(), 
                "tam": self.cb_tam.get(),
                "custo": self.ent_custo.get().replace(",", "."),
                "venda": self.ent_venda.get().replace(",", "."),
                "qtd": self.ent_qtd.get().strip(),
                "cat": self.cb_cat.get(), 
                "mat": self.cb_mat.get(),
                "forn": self.ent_forn.get().strip(),
                "status": self.var_status.get()
            }

            if not all([d["produto"], d["cor"], d["custo"], d["qtd"]]):
                messagebox.showwarning("Atenção", "Preencha os campos obrigatórios.")
                return

            if self.produto_id:
                database.atualizar_produto(
                    self.produto_id, sku=d["sku"], produto=d["produto"], cor=d["cor"], 
                    tamanho=d["tam"], precocusto=d["custo"], precovenda=d["venda"], 
                    quantidade=d["qtd"], categoria=d["cat"], material=d["mat"], 
                    fornecedor=d["forn"], status_item=d["status"]
                )
                messagebox.showinfo("Sucesso", "Produto atualizado!")
            else:
                database.cadastrar_produto(
                    d["sku"], d["produto"], d["cor"], d["tam"], 
                    d["custo"], d["venda"], d["qtd"], d["cat"], d["mat"], d["forn"]
                )
                messagebox.showinfo("Sucesso", "Produto cadastrado!")
            
            if hasattr(self.master, "exibir_produtos"):
                self.master.exibir_produtos()
            
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def preencher_dados(self, d):
        self.produto_id = d[0]
        self.ent_sku.delete(0, tk.END); self.ent_sku.insert(0, d[1] if d[1] else "")
        self.ent_produto.delete(0, tk.END); self.ent_produto.insert(0, d[2])
        self.cb_cor.set(d[3]); self.cb_tam.set(str(d[4]))
        self.ent_custo.delete(0, tk.END); self.ent_custo.insert(0, f"{d[5]:.2f}")
        self.ent_venda.delete(0, tk.END); self.ent_venda.insert(0, f"{d[6]:.2f}")
        self.ent_qtd.delete(0, tk.END); self.ent_qtd.insert(0, d[7])
        self.cb_cat.set(d[8]); self.cb_mat.set(d[9])
        self.ent_forn.delete(0, tk.END); self.ent_forn.insert(0, d[10] if d[10] else "")
        self.var_status.set(d[11])

        self.btn_salvar.config(text="ATUALIZAR PRODUTO", bg=self.cor_hover_field)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroProdutos(root)
    root.mainloop()