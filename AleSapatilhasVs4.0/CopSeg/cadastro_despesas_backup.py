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
        
        # --- Aplicar dimensões padrão (600px largura) ---
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=600, altura_desejada=820)
        
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

        # --- Título ---
        tk.Label(main_frame, text="Ficha Cadastro Despesa", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # --- BUSCA RÁPIDA (Conforme Cadastro Produtos) ---
        tk.Label(main_frame, text="🔍 BUSCA RÁPIDA", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
        self.ent_busca_interna = tk.Entry(main_frame, font=("Segoe UI", 9), bg=self.bg_card, relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_busca_interna.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, ipady=3, pady=5)
        self.ent_busca_interna.bind("<KeyRelease>", self.filtrar_busca_interna)
        
        self.tree_busca = ttk.Treeview(main_frame, columns=("id", "ent", "desc", "valor"), show="headings", height=3)
        self.tree_busca.heading("id", text="ID"); self.tree_busca.heading("ent", text="FORNECEDOR")
        self.tree_busca.heading("desc", text="DESCRIÇÃO"); self.tree_busca.heading("valor", text="VALOR")
        for col in ("id", "ent", "desc", "valor"): self.tree_busca.column(col, width=80, anchor="w")
        self.tree_busca.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5, padx=5)
        self.tree_busca.bind("<<TreeviewSelect>>", self.selecionar_da_busca)

        # --- FORMULÁRIO ---
        self.ent_entidade = criar_campo(main_frame, "FORNECEDOR*", 3, 0, colspan=3)
        self.ent_desc = criar_campo(main_frame, "DESCRIÇÃO DA DESPESA*", 5, 0, colspan=3)

        # Linha de Valores e Datas
        self.ent_valor = criar_campo(main_frame, "VALOR (R$)*", 7, 0)
        self.ent_valor.bind("<KeyRelease>", lambda e: self.atualizar_calculo_parcela())
        self.ent_vencimento = criar_campo(main_frame, "VENCIMENTO (DD/MM/AAAA)*", 7, 1)
        self.ent_vencimento.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(main_frame, text="STATUS*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9, "bold")).grid(row=7, column=2, sticky="w", padx=5)
        self.cb_status = ttk.Combobox(main_frame, values=self.list_status, state="readonly", font=("Segoe UI", 9))
        self.cb_status.set("Pendente")
        self.cb_status.grid(row=8, column=2, sticky="ew", padx=5, ipady=3)

        # Linha de Configurações 
        tk.Label(main_frame, text="CATEGORIA*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9, "bold")).grid(row=9, column=0, sticky="w", padx=5)
        self.cb_cat = ttk.Combobox(main_frame, values=self.list_categorias, state="readonly", font=("Segoe UI", 9))
        self.cb_cat.grid(row=10, column=0, sticky="ew", padx=5, ipady=3)

        tk.Label(main_frame, text="FORMA", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9, "bold")).grid(row=9, column=1, sticky="w", padx=5)
        self.cb_forma = ttk.Combobox(main_frame, values=self.list_formas, state="readonly", font=("Segoe UI", 9))
        self.cb_forma.set("Dinheiro")
        self.cb_forma.grid(row=10, column=1, sticky="ew", padx=5, ipady=3)

        tk.Label(main_frame, text="RECORRÊNCIA", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9, "bold")).grid(row=9, column=2, sticky="w", padx=5)
        self.cb_recorrencia = ttk.Combobox(main_frame, values=self.list_recorrencia, state="readonly", font=("Segoe UI", 9))
        self.cb_recorrencia.set("Não Recorrente")
        self.cb_recorrencia.grid(row=10, column=2, sticky="ew", padx=5, ipady=3)
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
        tk.Label(main_frame, text="HISTÓRICO / DETALHES DAS PARCELAS", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 8, "bold")).grid(row=12, column=0, columnspan=3, sticky="w", pady=(15, 2), padx=5)
        self.tree_pagos = ttk.Treeview(main_frame, columns=("parc", "venc", "pagto", "valor", "forma", "status"), show="headings", height=5, style="Hist.Treeview")
        
        headers = {"parc": "Nº", "venc": "VENC.", "pagto": "PAGTO", "valor": "VALOR", "forma": "FORMA", "status": "STATUS"}
        for col, text in headers.items():
            self.tree_pagos.heading(col, text=text)
            self.tree_pagos.column(col, width=80, anchor="center")
        self.tree_pagos.grid(row=13, column=0, columnspan=3, sticky="ew", padx=5)

        # --- BOTÕES (Dual Mode e Hover) ---
        texto_btn = "ATUALIZAR DESPESA" if self.despesa_id else "SALVAR DESPESA"
        self.btn_salvar = tk.Button(main_frame, text=texto_btn, bg=self.cor_btn_acao, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.validar_e_salvar)
        self.btn_salvar.grid(row=14, column=0, columnspan=3, pady=(10, 0), sticky="ew", ipady=6)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.destroy)
        self.btn_cancelar.grid(row=15, column=0, columnspan=3, pady=(10, 0), sticky="ew", ipady=6)

        # Bind Hovers
        self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_acao))
        self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        self.atualizar_tree_busca()

    # --- LÓGICA ---
    def toggle_parcelas(self, event):
        if self.cb_recorrencia.get() == "Parcelar":
            self.frame_parcelas.grid(row=11, column=0, columnspan=3, sticky="ew", pady=5)
        else: self.frame_parcelas.grid_forget()

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
            messagebox.showwarning("Erro", "Preencha os campos obrigatórios (*)")
            return

        try:
            if self.despesa_id:
                database.atualizar_financeiro(self.despesa_id, entidade_nome=d["ent"], descricao=d["desc"], valor=d["val"], data_vencimento=d["venc"], forma_pagamento=d["forma"], categoria=d["cat"], status=d["status"])
                messagebox.showinfo("Sucesso", "Despesa atualizada!")
            else:
                parc = int(self.ent_qtd_parc.get()) if self.cb_recorrencia.get() == "Parcelar" else 1
                database.lancar_despesa(d["desc"], float(d["val"]), d["cat"], d["venc"], parc)
                # Nota: Adicionar entidade_nome na sua função database.lancar_despesa se necessário
                messagebox.showinfo("Sucesso", "Nova despesa cadastrada!")
            
            if hasattr(self.master, "exibir_financeiro"): self.master.exibir_financeiro()
            self.destroy()
        except Exception as e: messagebox.showerror("Erro", str(e))

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

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroDespesas(root)
    root.mainloop()

