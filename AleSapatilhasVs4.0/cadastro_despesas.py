import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import database 
import ui_utils

class JanelaCadastroDespesas(tk.Toplevel):
    def __init__(self, master, dados_despesa=None):
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
        self.title("Alê Sapatilhas - Gestão Financeira")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)
        
        self._manter_em_primeiro_plano()
        
        # --- Aplicar dimensões padrão (600px largura, altura aumentada) ---
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=600, altura_desejada=780)
        
        self.despesa_id = dados_despesa[0] if dados_despesa else None
        
        self.list_formas = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Boleto", "Outros"]
        self.list_categorias = ["Infraestrutura", "Compra Mercadoria", "Marketing", "Salários", "Impostos", "Outros"]
        self.list_recorrencia = ["Não Recorrente", "Fixa Mensal", "Parcelar"]
        self.list_status = ["Pendente", "Pago", "Atrasado", "Cancelado"]

        self.setup_styles()
        self.criar_widgets()
        
        if dados_despesa:
            self.preencher_dados(dados_despesa)
            
        self.grab_set()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.bg_card, background=self.bg_card, 
                        arrowcolor=self.cor_btn_acao, bordercolor=self.cor_borda)
        style.configure("Busca.Treeview", background="#F8FAFC", rowheight=22, font=("Segoe UI", 9))

    def formatar_data_para_bd(self, data_str):
        try:
            return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except: return None

    def _manter_em_primeiro_plano(self):
        try:
            self.attributes("-topmost", True)
        except Exception as e:
            messagebox.showwarning("Aviso", f"Não foi possível manter esta janela em primeiro plano: {e}", parent=self)

    def criar_widgets(self):
        wrapper = tk.Frame(self, bg=self.bg_fundo)
        wrapper.pack(fill="both", expand=True)

        canvas = tk.Canvas(wrapper, bg=self.bg_fundo, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        main_frame = tk.Frame(canvas, bg=self.bg_fundo, padx=20, pady=10)
        self.canvas_frame = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", _update_scroll_region)
        def _resize_frame(event):
            canvas.itemconfigure(self.canvas_frame, width=event.width)
        canvas.bind("<Configure>", _resize_frame)

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
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(2, 0), padx=5)
            ent = tk.Entry(parent, font=("Segoe UI", 9), bg=self.bg_card, fg=self.cor_texto,
                            relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=2, padx=(5, 10) if col < 2 else 5)
            aplicar_estilo_foco(ent)
            return ent

        # --- Título ---
        tk.Label(main_frame, text=" Lançamento de Despesa", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # --- BUSCA RÁPIDA (Conforme Cadastro Produtos) ---
        tk.Label(main_frame, text="🔍 BUSCA RÁPIDA", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
        self.ent_busca_interna = tk.Entry(main_frame, font=("Segoe UI", 9), bg=self.bg_card, relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_busca_interna.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, ipady=3, pady=5)
        self.ent_busca_interna.bind("<KeyRelease>", self.filtrar_busca_interna)
        self.ent_busca_interna.bind("<Enter>", lambda e: self.ent_busca_interna.focus_set())
        
        self.tree_busca = ttk.Treeview(main_frame, columns=("id", "ent", "desc", "valor"), show="headings", height=2, style="Busca.Treeview")
        self.tree_busca.heading("id", text="ID"); self.tree_busca.heading("ent", text="FORNECEDOR")
        self.tree_busca.heading("desc", text="DESCRIÇÃO"); self.tree_busca.heading("valor", text="VALOR")
        for col in ("id", "ent", "desc", "valor"): self.tree_busca.column(col, width=80, anchor="w")
        self.tree_busca.grid(row=3, column=0, columnspan=3, sticky="ew", pady=2, padx=5)
        self.tree_busca.bind("<<TreeviewSelect>>", self.selecionar_da_busca)
        self.tree_busca.bind("<Double-1>", self.editar_despesa_duplo_clique)
        self.tree_busca.bind("<Button-3>", self.menu_contexto)

        # --- FORMULÁRIO ---
        self.ent_entidade = criar_campo(main_frame, "FORNECEDOR*", 4, 0, colspan=3)
        self.ent_desc = criar_campo(main_frame, "DESCRIÇÃO DA DESPESA*", 6, 0, colspan=3)

        # Linha de Valores e Datas
        self.ent_valor = criar_campo(main_frame, "VALOR (R$)*", 8, 0)
        self.ent_valor.bind("<KeyRelease>", lambda e: self.atualizar_calculo_parcela())
        self.ent_vencimento = criar_campo(main_frame, "VENCIMENTO (DD/MM/AAAA)*", 8, 1)
        self.ent_vencimento.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(main_frame, text="STATUS*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=8, column=2, sticky="w", padx=5)
        self.cb_status = ttk.Combobox(main_frame, values=self.list_status, state="readonly", font=("Segoe UI", 9))
        self.cb_status.set("Pendente")
        self.cb_status.grid(row=9, column=2, sticky="ew", padx=5, ipady=2)

        # Linha de Configurações 
        tk.Label(main_frame, text="CATEGORIA*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=10, column=0, sticky="w", padx=5)
        self.cb_cat = ttk.Combobox(main_frame, values=self.list_categorias, state="readonly", font=("Segoe UI", 9))
        self.cb_cat.grid(row=11, column=0, sticky="ew", padx=5, ipady=2)

        tk.Label(main_frame, text="FORMA DE PAGAMENTO", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=10, column=1, sticky="w", padx=5)
        self.cb_forma = ttk.Combobox(main_frame, values=self.list_formas, state="readonly", font=("Segoe UI", 9))
        self.cb_forma.set("Dinheiro")
        self.cb_forma.grid(row=11, column=1, sticky="ew", padx=5, ipady=2)

        tk.Label(main_frame, text="RECORRÊNCIA", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=10, column=2, sticky="w", padx=5)
        self.cb_recorrencia = ttk.Combobox(main_frame, values=self.list_recorrencia, state="readonly", font=("Segoe UI", 9))
        self.cb_recorrencia.set("Não Recorrente")
        self.cb_recorrencia.grid(row=11, column=2, sticky="ew", padx=5, ipady=2)
        self.cb_recorrencia.bind("<<ComboboxSelected>>", self.toggle_parcelas)

        # Sub-menu Parcelas
        self.frame_parcelas = tk.Frame(main_frame, bg="#E2E8F0", pady=5, padx=10)
        tk.Label(self.frame_parcelas, text="PARCELAS:", bg="#E2E8F0", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.ent_qtd_parc = tk.Entry(self.frame_parcelas, width=5)
        self.ent_qtd_parc.pack(side="left", padx=5)
        self.ent_qtd_parc.insert(0, "1")
        self.ent_qtd_parc.bind("<KeyRelease>", lambda e: self.atualizar_calculo_parcela())
        self.lbl_calculo = tk.Label(self.frame_parcelas, text="= 1x R$ 0.00", bg="#E2E8F0", font=("Segoe UI", 9, "italic"), fg=self.cor_destaque)
        self.lbl_calculo.pack(side="left", padx=10)

        # --- TREEVIEW HISTÓRICO ---
        tk.Label(main_frame, text="HISTÓRICO DAS PARCELAS", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 8, "bold")).grid(row=13, column=0, columnspan=3, sticky="w", pady=(15, 2), padx=5)
        self.tree_pagos = ttk.Treeview(main_frame, columns=("parc", "venc", "pagto", "valor", "forma", "status"), show="headings", height=3, style="Hist.Treeview")
        
        headers = {"parc": "Nº", "venc": "VENC.", "pagto": "PAGTO", "valor": "VALOR", "forma": "FORMA", "status": "STATUS"}
        for col, text in headers.items():
            self.tree_pagos.heading(col, text=text)
            self.tree_pagos.column(col, width=80, anchor="center")
        self.tree_pagos.grid(row=14, column=0, columnspan=3, sticky="ew", padx=5)

        # --- BOTÕES (Dual Mode e Hover) ---
        texto_btn = "ATUALIZAR DESPESA" if self.despesa_id else "SALVAR DESPESA"
        self.btn_salvar = tk.Button(main_frame, text=texto_btn, bg=self.cor_btn_acao, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.validar_e_salvar)
        self.btn_salvar.grid(row=15, column=0, columnspan=3, pady=(10, 0), sticky="ew", ipady=6)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.destroy)
        self.btn_cancelar.grid(row=16, column=0, columnspan=3, pady=(10, 0), sticky="ew", ipady=6)

        # Bind Hovers
        self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_acao))
        self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        # --- Menu de contexto (botão direito) ---
        self.menu_contexto = tk.Menu(self, tearoff=0)
        self.menu_contexto.add_command(label="Editar", command=self.editar_despesa_menu)
        self.menu_contexto.add_command(label="Quitar", command=self.quitar_despesa_menu)
        self.menu_contexto.add_command(label="Restaurar", command=self.restaurar_despesa_menu)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label="Sair", command=self.destroy)

        self.atualizar_tree_busca()

    # --- LÓGICA ---
    def toggle_parcelas(self, event):
        if self.cb_recorrencia.get() == "Parcelar":
            self.frame_parcelas.grid(row=12, column=0, columnspan=3, sticky="ew", pady=5)
        else:
            self.frame_parcelas.grid_forget()

    def atualizar_calculo_parcela(self):
        try:
            v = float(self.ent_valor.get().replace(",", "."))
            q = int(self.ent_qtd_parc.get())
            self.lbl_calculo.config(text=f"= {q}x R$ {(v/q):.2f}")
        except: self.lbl_calculo.config(text="= Erro no cálculo")

    def atualizar_tree_busca(self):
        self.tree_busca.delete(*self.tree_busca.get_children())
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, entidade_nome, descricao, valor FROM financeiro WHERE tipo='Despesa' LIMIT 20")
            for d in cursor.fetchall(): self.tree_busca.insert("", "end", values=d)

    def filtrar_busca_interna(self, e):
        t = self.ent_busca_interna.get().lower()
        self.tree_busca.delete(*self.tree_busca.get_children())
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, entidade_nome, descricao, valor FROM financeiro WHERE tipo='Despesa' AND (entidade_nome LIKE ? OR descricao LIKE ?)", (f'%{t}%', f'%{t}%'))
            for d in cursor.fetchall(): self.tree_busca.insert("", "end", values=d)

    def selecionar_da_busca(self, e):
        sel = self.tree_busca.selection()
        if not sel: return
        id_d = self.tree_busca.item(sel)["values"][0]
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM financeiro WHERE id=?", (id_d,))
            self.preencher_dados(cursor.fetchone())

    def validar_e_salvar(self):
        # --- Lógica de persistência DUAL ---
        d = {
            "ent": self.ent_entidade.get(), "desc": self.ent_desc.get(),
            "val": self.ent_valor.get().replace(",", "."), "venc": self.formatar_data_para_bd(self.ent_vencimento.get()),
            "forma": self.cb_forma.get(), "cat": self.cb_cat.get(), "status": self.cb_status.get()
        }
        
        if not all([d["ent"], d["desc"], d["val"], d["venc"]]):
            messagebox.showwarning("Erro", "Preencha os campos obrigatórios (*)", parent=self)
            return

        try:
            if self.despesa_id:
                database.atualizar_despesa(self.despesa_id, entidade_nome=d["ent"], descricao=d["desc"], valor=d["val"], data_vencimento=d["venc"], forma_pagamento=d["forma"], categoria=d["cat"], status=d["status"])
                messagebox.showinfo("Sucesso", "Despesa atualizada!", parent=self)
            else:
                parc = int(self.ent_qtd_parc.get()) if self.cb_recorrencia.get() == "Parcelar" else 1
                sucesso, mensagem = database.cadastrar_despesa(d["ent"], d["desc"], d["cat"], float(d["val"]), self.cb_recorrencia.get(), d["venc"], d["forma"], d["status"], parc)
                if not sucesso:
                    messagebox.showerror("Erro", mensagem, parent=self)
                    return
                messagebox.showinfo("Sucesso", "Nova despesa cadastrada!", parent=self)
            
            if hasattr(self.master, "exibir_financeiro"): self.master.exibir_financeiro()
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", str(e), parent=self)

    def preencher_dados(self, d):
        # d vem da tabela financeiro: (id, tipo, venda_id, entidade, desc, valor, parc_at, parc_tot, venc, pagto, forma, cat, status)
        self.despesa_id = d[0]
        self.ent_entidade.delete(0, tk.END); self.ent_entidade.insert(0, d[3] if d[3] else "")
        self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, d[4])
        self.ent_valor.delete(0, tk.END); self.ent_valor.insert(0, f"{d[5]:.2f}")
        venc_br = datetime.strptime(d[8], "%Y-%m-%d").strftime("%d/%m/%Y")
        self.ent_vencimento.delete(0, tk.END); self.ent_vencimento.insert(0, venc_br)
        self.cb_forma.set(d[10] if d[10] else "Dinheiro")
        self.cb_cat.set(d[11] if d[11] else "Outros")
        self.cb_status.set(d[12])
        self.btn_salvar.config(text="ATUALIZAR DESPESA", bg=self.cor_hover_field)

    def editar_despesa_duplo_clique(self, event):
        """Editar despesa/receita com duplo clique - distingue tipo"""
        sel = self.tree_busca.selection()
        if not sel: return
        id_item = self.tree_busca.item(sel)["values"][0]
        
        # Verificar se é receita ou despesa
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tipo, venda_id FROM financeiro WHERE id=?", (id_item,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Erro", "Registro financeiro não encontrado.", parent=self)
                return
            tipo, venda_id = result
        
        if tipo == "Receita":
            if not venda_id:
                messagebox.showerror("Erro", "Registro de receita sem venda vinculada.", parent=self)
                return
            from cadastro_vendas import JanelaCadastroVendas
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.id, c.nome, c.telefone, GROUP_CONCAT(p.produto), v.valor_total, v.forma_pagamento, v.qtd_parcelas, v.desconto, v.data_venda
                    FROM vendas v
                    JOIN clientes c ON v.cliente_id = c.id
                    JOIN itens_venda vi ON v.id = vi.venda_id
                    JOIN produtos p ON vi.produto_id = p.id
                    WHERE v.id = ?
                    GROUP BY v.id
                """, (venda_id,))
                dados_venda = cursor.fetchone()

            if dados_venda:
                dados_venda_dict = {
                    'id': dados_venda[0],
                    'cliente': f"{dados_venda[1]} - {dados_venda[2]}",
                    'produtos': dados_venda[3],
                    'total': dados_venda[4],
                    'forma': dados_venda[5],
                    'parcelas': dados_venda[6],
                    'desconto': dados_venda[7],
                    'data': dados_venda[8]
                }
                JanelaCadastroVendas(self.master, dados_venda=dados_venda_dict)
            else:
                messagebox.showinfo("Info", "Venda não encontrada para o registro selecionado.", parent=self)
        else:
            with database.conectar() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM financeiro WHERE id=?", (id_item,))
                dados = cursor.fetchone()
                if dados:
                    self.preencher_dados(dados)
                else:
                    messagebox.showerror("Erro", "Despesa não encontrada.", parent=self)

    def menu_contexto(self, event):
        """Mostrar menu de contexto no botão direito"""
        try:
            self.tree_busca.selection_set(self.tree_busca.identify_row(event.y))
            self.menu_contexto.post(event.x_root, event.y_root)
        except:
            pass

    def editar_despesa_menu(self):
        """Editar despesa/receita via menu de contexto"""
        self.editar_despesa_duplo_clique(None)

    def quitar_despesa_menu(self):
        """Quitar despesa via menu de contexto"""
        sel = self.tree_busca.selection()
        if not sel: return
        id_d = self.tree_busca.item(sel)["values"][0]
        
        if messagebox.askyesno("Confirmar", "Deseja quitar esta despesa?"):
            try:
                database.quitar_titulo_financeiro(id_d, "Diversos")
                messagebox.showinfo("Sucesso", "Despesa quitada!", parent=self)
                self.atualizar_tree_busca()
                if hasattr(self.master, "exibir_financeiro"): 
                    self.master.exibir_financeiro()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao quitar despesa: {str(e)}", parent=self)

    def restaurar_despesa_menu(self):
        """Restaurar despesa via menu de contexto"""
        sel = self.tree_busca.selection()
        if not sel: return
        id_d = self.tree_busca.item(sel)["values"][0]
        
        # Buscar status atual
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM financeiro WHERE id=?", (id_d,))
            status_atual = cursor.fetchone()[0]
        
        # Definir status anterior baseado no atual
        if status_atual == "Pago":
            novo_status = "Pendente"
        elif status_atual == "Cancelado":
            novo_status = "Pendente"
        elif status_atual == "Atrasado":
            novo_status = "Pendente"
        else:
            messagebox.showinfo("Info", "Não há status anterior para restaurar.", parent=self)
            return
        
        if messagebox.askyesno("Confirmar", f"Restaurar despesa para '{novo_status}'?"):
            try:
                database.atualizar_financeiro(id_d, status=novo_status)
                messagebox.showinfo("Sucesso", "Despesa restaurada!", parent=self)
                self.atualizar_tree_busca()
                if hasattr(self.master, "exibir_financeiro"): 
                    self.master.exibir_financeiro()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao restaurar despesa: {str(e)}", parent=self)


class VisualizarRecibo(tk.Toplevel):
    """Classe para visualizar recibo de venda"""
    def __init__(self, master, id_venda):
        super().__init__(master)
        
        # --- Paleta de cores ---
        paleta = ui_utils.get_paleta()
        self.bg_fundo = paleta["bg_fundo"]
        self.bg_card = paleta["bg_card"]
        self.cor_texto = paleta["cor_texto"]
        self.cor_destaque = paleta["cor_destaque"]
        
        self.title("Recibo de Venda")
        self.configure(bg=self.bg_fundo)
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=400, altura_desejada=500)
        
        # Buscar dados da venda
        with database.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id, c.nome, c.telefone, v.total, v.forma_pagamento, v.parcelas, v.desconto, v.data_venda,
                       GROUP_CONCAT(CONCAT(p.produto, ' (', vi.qtd, 'x R$ ', vi.preco_unitario, ')')) as produtos
                FROM vendas v
                JOIN clientes c ON v.cliente_id = c.id
                JOIN vendas_itens vi ON v.id = vi.venda_id
                JOIN produtos p ON vi.produto_id = p.id
                WHERE v.id = ?
                GROUP BY v.id
            """, (id_venda,))
            dados = cursor.fetchone()
        
        if not dados:
            messagebox.showerror("Erro", "Venda não encontrada!", parent=self)
            self.destroy()
            return
        
        # Criar interface
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="🧾 RECIBO DE VENDA", bg=self.bg_fundo, 
                 fg=self.cor_destaque, font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        
        # Informações da venda
        info_text = f"""
ID da Venda: {dados[0]}
Cliente: {dados[1]}
Telefone: {dados[2]}
Data: {dados[7]}

Produtos:
{dados[8].replace(',', '\n')}

Forma de Pagamento: {dados[4]}
Parcelas: {dados[5]}x
Desconto: R$ {dados[6]:.2f}

TOTAL: R$ {dados[3]:.2f}
        """
        
        lbl_info = tk.Label(main_frame, text=info_text.strip(), bg=self.bg_card, fg=self.cor_texto,
                           font=("Courier New", 10), justify="left", relief="solid", borderwidth=1)
        lbl_info.pack(fill="both", expand=True, pady=(0, 20))
        
        # Botão fechar
        tk.Button(main_frame, text="FECHAR", bg=self.cor_destaque, fg="white",
                 font=("Segoe UI", 10, "bold"), command=self.destroy).pack()
        
        self.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroDespesas(root)
    root.mainloop()

