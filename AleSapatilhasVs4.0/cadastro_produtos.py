import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import database 
import ui_utils
import os

class JanelaCadastroProdutos(tk.Toplevel):
    def __init__(self, master, dados_produto=None):
        super().__init__(master)
        
        # --- Paleta de cores ---
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
        self.cor_hover_field = paleta["cor_hover_field"]

        # --- Configurações da janela ---
        self.title("Alê Sapatilhas - Gestão do Estoque")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)
        
        # --- Aplicar dimensões padrão (600px largura, altura aumentada) ---
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=600, altura_desejada=1000)

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
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Helpers de estilo (Hover e Input) ---
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

        def criar_campo(parent, texto, row, col=0, colspan=2):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(3, 0))
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                            relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=3, padx=(0, 5) if colspan==1 else 0)
            aplicar_estilo_foco(ent)
            return ent

        def criar_combo(parent, texto, lista, row, col, span=1):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(3, 0))
            combo = ttk.Combobox(parent, values=lista, font=("Segoe UI", 10), state="readonly")
            combo.set(lista[0])
            combo.grid(row=row+1, column=col, columnspan=span, sticky="ew", padx=(0, 5) if col==0 else 0)
            return combo

        tk.Label(main_frame, text="Ficha Cadastral do Produto", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

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

        self.ent_produto = criar_campo(main_frame, "DESCRIÇÃO DO MODELO*", 5)
        self.cb_cat      = criar_combo(main_frame, "CATEGORIA*", self.list_categorias, 7, 0)
        self.cb_mat      = criar_combo(main_frame, "MATERIAL", self.list_materiais, 7, 1)

        self.ent_custo = criar_campo(main_frame, "PREÇO DE CUSTO (R$)*", 9, col=0, colspan=1)
        self.ent_custo.bind("<KeyRelease>", self.calcular_markup)
        
        tk.Label(main_frame, text="PREÇO DE VENDA (R$)*", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=9, column=1, sticky="w", pady=(3, 0))
        self.ent_venda = tk.Entry(main_frame, font=("Segoe UI", 10, "bold"), bg="#E2E8F0", fg=self.cor_destaque, 
                                  relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_venda.grid(row=10, column=1, sticky="ew", ipady=3)

        self.ent_forn = criar_campo(main_frame, "FORNECEDOR*", 11)

        # --- Campo Data do Lançamento ---
        tk.Label(main_frame, text="DATA DO LANÇAMENTO", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=13, column=0, sticky="w", pady=(3, 0))
        self.ent_data_lancamento = tk.Entry(main_frame, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                                           relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_data_lancamento.grid(row=14, column=0, sticky="ew", ipady=3, padx=(0, 5))
        self.ent_data_lancamento.insert(0, datetime.now().strftime("%d/%m/%Y"))
        aplicar_estilo_foco(self.ent_data_lancamento)

        # --- Campo Status do Produto ---
        tk.Label(main_frame, text="STATUS DO PRODUTO*", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=13, column=1, sticky="w", pady=(3, 0))
        self.var_status_produto = tk.StringVar(value="Disponível")
        self.opt_status_produto = tk.OptionMenu(main_frame, self.var_status_produto, "Disponível", "Indisponível", "Esgotado", "Promocional")
        self.opt_status_produto.config(bg=self.bg_card, fg=self.cor_texto, relief="flat", highlightthickness=1, 
                                      highlightbackground=self.cor_borda, font=("Segoe UI", 10), cursor="hand2")
        self.opt_status_produto.grid(row=14, column=1, sticky="ew", pady=(1, 0))

        # --- GRADE DE ESTOQUE E FOTO ---
        tk.Label(main_frame, text="GRADE DE ESTOQUE", bg=self.bg_fundo, fg=self.cor_texto, 
                 font=("Segoe UI", 9, "bold")).grid(row=15, column=0, sticky="w", pady=(10, 2))
        
        tk.Label(main_frame, text="FOTO DO PRODUTO", bg=self.bg_fundo, fg=self.cor_texto, 
                 font=("Segoe UI", 9, "bold")).grid(row=15, column=1, sticky="w", pady=(10, 2))
        
        # Frame para grade e foto lado a lado
        frame_conteudo = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_conteudo.grid(row=16, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        frame_conteudo.columnconfigure(0, weight=1)
        frame_conteudo.columnconfigure(1, weight=1)

        # --- GRADE DE ESTOQUE (lado esquerdo) ---
        frame_grade = tk.LabelFrame(frame_conteudo, bg=self.bg_card, relief="groove", borderwidth=1, padx=10, pady=10, text="Estoque")
        frame_grade.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        frame_grade.columnconfigure(0, weight=1)

        self.cb_cor = criar_combo(frame_grade, "COR*", self.list_cores, 0, 0, 2)
        self.cb_tam = criar_combo(frame_grade, "TAMANHO*", self.list_tamanhos, 2, 0, 2)
        self.ent_qtd = criar_campo(frame_grade, "QUANTIDADE*", 4, col=0, colspan=1)
        
        tk.Label(frame_grade, text="STATUS DO ITEM*", bg=self.bg_card, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=4, column=1, sticky="w", pady=(3, 0))
        self.var_status = tk.StringVar(value="Disponível")
        self.opt_status = tk.OptionMenu(frame_grade, self.var_status, *self.list_status)
        self.opt_status.config(bg=self.bg_card, fg=self.cor_texto, relief="flat", highlightthickness=1, 
                                highlightbackground=self.cor_borda, font=("Segoe UI", 10), cursor="hand2")
        self.opt_status.grid(row=5, column=1, sticky="ew", pady=(1, 0))

        # --- ESPAÇO PARA FOTO (lado direito) ---
        frame_foto = tk.LabelFrame(frame_conteudo, bg=self.bg_card, relief="groove", borderwidth=1, padx=10, pady=10, text="Foto")
        frame_foto.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Placeholder para foto
        self.lbl_foto = tk.Label(frame_foto, text="📷\n\nClique para\nadicionar foto", 
                                bg="#F8FAFC", fg=self.cor_texto, font=("Segoe UI", 10), 
                                relief="flat", cursor="hand2", width=15, height=6)
        self.lbl_foto.pack(expand=True, fill="both", padx=5, pady=5)
        self.lbl_foto.bind("<Button-1>", self.selecionar_foto)

        # --- Campo SKU (no final, apenas visualização) ---
        tk.Label(main_frame, text="CÓDIGO DO PRODUTO (SKU)", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=17, column=0, sticky="w", pady=(10, 0))
        self.ent_sku = tk.Entry(main_frame, font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg=self.cor_destaque, 
                               relief="flat", highlightbackground=self.cor_borda, highlightthickness=1, state="readonly")
        self.ent_sku.grid(row=18, column=0, columnspan=2, sticky="ew", ipady=3, pady=(0, 10))
        
        # --- BOTÕES (Dual Mode e Hover) ---
        texto_botao = "ATUALIZAR PRODUTO" if self.produto_id else "SALVAR PRODUTO"
        cor_base_acao = self.cor_hover_field if self.produto_id else self.cor_btn_acao

        self.btn_salvar = tk.Button(main_frame, text=texto_botao, bg=cor_base_acao, fg="white", 
                                    font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                    command=self.validar_e_salvar)
        self.btn_salvar.grid(row=19, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=6)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", 
                                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                      command=self.destroy)
        self.btn_cancelar.grid(row=20, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=6)

        self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=cor_base_acao))
        self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        # --- Menu de contexto (botão direito) ---
        self.menu_contexto = tk.Menu(self, tearoff=0)
        self.menu_contexto.add_command(label="Editar", command=self.editar_produto_menu)
        self.menu_contexto.add_command(label="Indisponibilizar", command=self.indisponibilizar_produto_menu)
        self.menu_contexto.add_command(label="Promocional", command=self.promocional_produto_menu)
        self.menu_contexto.add_command(label="Restaurar", command=self.restaurar_produto_menu)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label="Sair", command=self.destroy)

        # Bindings para treeview
        self.tree_busca.bind("<Double-1>", self.editar_produto_duplo_clique)
        self.tree_busca.bind("<Button-3>", self.menu_contexto_produto)

        self.atualizar_tree_busca()
        self.gerar_sku_automatico()  # Gerar SKU inicial

    def calcular_markup(self, event=None):
        try:
            custo = self.ent_custo.get().replace(",", ".")
            if custo:
                venda = float(custo) * 2.5
                self.ent_venda.delete(0, tk.END)
                self.ent_venda.insert(0, f"{venda:.2f}")
        except ValueError:
            self.ent_venda.delete(0, tk.END)

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
        # Correção aqui: garantindo que a conexão e preenchimento funcionem
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_prod,))
            dados = cursor.fetchone()
            if dados: 
                self.preencher_dados(dados)

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

    def gerar_sku_automatico(self):
        """Gera SKU automaticamente baseado nos dados do produto"""
        produto = self.ent_produto.get().strip()[:3].upper() if self.ent_produto.get().strip() else "XXX"
        cor = self.cb_cor.get()[:2].upper() if self.cb_cor.get() else "XX"
        tam = self.cb_tam.get() if self.cb_tam.get() else "XX"
        categoria = self.cb_cat.get()[:2].upper() if self.cb_cat.get() else "XX"
        
        # Formato: PRODUTO-COR-TAMANHO-CATEGORIA
        sku = f"{produto}-{cor}-{tam}-{categoria}"
        self.ent_sku.config(state="normal")
        self.ent_sku.delete(0, tk.END)
        self.ent_sku.insert(0, sku)
        self.ent_sku.config(state="readonly")

    def selecionar_foto(self, event):
        """Selecionar foto da galeria e copiar para pasta images"""
        # Abrir diálogo para selecionar arquivo
        caminho_origem = filedialog.askopenfilename(
            title="Selecionar Foto do Produto",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp"), ("Todos os arquivos", "*.*")]
        )
        
        if caminho_origem:
            try:
                # Criar pasta images se não existir
                os.makedirs("images", exist_ok=True)
                
                # Gerar nome único para a foto
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"produto_{timestamp}.jpg"
                caminho_destino = os.path.join("images", nome_arquivo)
                
                # Copiar arquivo para pasta images
                import shutil
                shutil.copy2(caminho_origem, caminho_destino)
                
                # Atualizar campo foto (se existir)
                if hasattr(self, 'caminho_foto'):
                    self.caminho_foto = caminho_destino
                
                # Atualizar label para mostrar preview
                self.lbl_foto.config(text=f"📷\n\nFoto selecionada:\n{nome_arquivo}", fg=self.cor_destaque)
                
                messagebox.showinfo("Sucesso", f"Foto '{nome_arquivo}' adicionada com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao copiar foto: {str(e)}")

    def editar_produto_duplo_clique(self, event):
        """Editar produto com duplo clique"""
        selecao = self.tree_busca.selection()
        if not selecao: return
        id_prod = self.tree_busca.item(selecao)["values"][0]
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_prod,))
            dados = cursor.fetchone()
            if dados:
                self.preencher_dados(dados)

    def menu_contexto_produto(self, event):
        """Mostrar menu de contexto no botão direito"""
        try:
            self.tree_busca.selection_set(self.tree_busca.identify_row(event.y))
            self.menu_contexto.post(event.x_root, event.y_root)
        except:
            pass

    def editar_produto_menu(self):
        """Editar produto via menu de contexto"""
        self.editar_produto_duplo_clique(None)

    def indisponibilizar_produto_menu(self):
        """Indisponibilizar produto via menu de contexto"""
        selecao = self.tree_busca.selection()
        if not selecao: return
        id_prod = self.tree_busca.item(selecao)["values"][0]
        
        if messagebox.askyesno("Confirmar", "Deseja indisponibilizar este produto?"):
            try:
                database.atualizar_produto(id_prod, status_item="Indisponível")
                messagebox.showinfo("Sucesso", "Produto indisponibilizado!")
                self.atualizar_tree_busca()
                if hasattr(self.master, "exibir_produtos"):
                    self.master.exibir_produtos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao indisponibilizar produto: {str(e)}")

    def promocional_produto_menu(self):
        """Marcar produto como promocional via menu de contexto"""
        selecao = self.tree_busca.selection()
        if not selecao: return
        id_prod = self.tree_busca.item(selecao)["values"][0]
        
        if messagebox.askyesno("Confirmar", "Deseja marcar este produto como promocional?"):
            try:
                database.atualizar_produto(id_prod, status_item="Promocional")
                messagebox.showinfo("Sucesso", "Produto marcado como promocional!")
                self.atualizar_tree_busca()
                if hasattr(self.master, "exibir_produtos"):
                    self.master.exibir_produtos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao marcar produto como promocional: {str(e)}")

    def restaurar_produto_menu(self):
        """Restaurar produto via menu de contexto"""
        selecao = self.tree_busca.selection()
        if not selecao: return
        id_prod = self.tree_busca.item(selecao)["values"][0]
        
        # Buscar status atual
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status_item FROM produtos WHERE id=?", (id_prod,))
            status_atual = cursor.fetchone()[0]
        
        # Definir status anterior baseado no atual
        if status_atual == "Indisponível":
            novo_status = "Disponível"
        elif status_atual == "Esgotado":
            novo_status = "Disponível"
        else:
            messagebox.showinfo("Info", "Não há status anterior para restaurar.")
            return
        
        if messagebox.askyesno("Confirmar", f"Restaurar produto para '{novo_status}'?"):
            try:
                database.atualizar_produto(id_prod, status_item=novo_status)
                messagebox.showinfo("Sucesso", "Produto restaurado!")
                self.atualizar_tree_busca()
                if hasattr(self.master, "exibir_produtos"):
                    self.master.exibir_produtos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao restaurar produto: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal para abrir apenas o Toplevel
    JanelaCadastroProdutos(root)
    root.mainloop()