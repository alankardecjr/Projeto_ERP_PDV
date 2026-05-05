import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
# import database  # Mantido conforme seu original

class JanelaCadastroDespesas(tk.Toplevel):
    def __init__(self, master, dados_despesa=None):
        super().__init__(master)

        # --- Paleta de cores ---
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

        # --- Configurações da Janela ---
        self.title("Alê Sapatilhas - Gestão Financeira")
        self.geometry("620x850")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)
        
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
        
        # Ajuste para o Combobox ter a mesma altura visual do Entry
        style.configure("TCombobox", 
                        fieldbackground=self.bg_card, 
                        background=self.bg_card, 
                        bordercolor=self.cor_borda,
                        lightcolor=self.cor_borda,
                        darkcolor=self.cor_borda,
                        arrowsize=15)
        
        style.map("TCombobox", fieldbackground=[('readonly', self.bg_card)])
        
        style.configure("Hist.Treeview", background="#F8FAFC", rowheight=25, font=("Segoe UI", 9))
        style.configure("Hist.Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def formatar_data_para_bd(self, data_str):
        try:
            return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except: return None

    def criar_widgets(self):
        # Frame centralizado
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Configurar colunas para centralização e expansão igual
        for i in range(3):
            main_frame.grid_columnconfigure(i, weight=1)

        def aplicar_estilo_foco(ent):
            def on_enter(e): ent.config(highlightbackground=self.cor_hover_field)
            def on_leave(e): ent.config(highlightbackground=self.cor_borda)
            ent.bind("<Enter>", on_enter)
            ent.bind("<Leave>", on_leave)

        def criar_campo(parent, texto, row, col, colspan=1):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=row, column=col, columnspan=colspan, sticky="w", pady=(8, 0), padx=5)
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            # ipady=5 garante que a altura interna seja igual ao do Combobox padrão
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=5, padx=5)
            aplicar_estilo_foco(ent)
            return ent

        # --- BUSCA RÁPIDA ---
        tk.Label(main_frame, text="🔍 BUSCA RÁPIDA", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=5)
        self.ent_busca_interna = tk.Entry(main_frame, font=("Segoe UI", 9), bg=self.bg_card, relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
        self.ent_busca_interna.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, ipady=4)
        
        self.tree_busca = ttk.Treeview(main_frame, columns=("id", "ent", "desc", "valor"), show="headings", height=3)
        for col, text in zip(("id", "ent", "desc", "valor"), ("ID", "FORNECEDOR", "DESCRIÇÃO", "VALOR")):
            self.tree_busca.heading(col, text=text)
            self.tree_busca.column(col, width=100, anchor="w")
        self.tree_busca.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(5, 15), padx=5)

        # --- FORMULÁRIO (Organizado e centralizado) ---
        self.ent_entidade = criar_campo(main_frame, "FORNECEDOR / ENTIDADE*", 3, 0, colspan=3)
        self.ent_desc = criar_campo(main_frame, "DESCRIÇÃO DA DESPESA*", 5, 0, colspan=3)

        # Linha de Valores, Datas e Status (Mesma Altura)
        self.ent_valor = criar_campo(main_frame, "VALOR (R$)*", 7, 0)
        self.ent_vencimento = criar_campo(main_frame, "VENCIMENTO*", 7, 1)
        self.ent_vencimento.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        tk.Label(main_frame, text="STATUS*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=7, column=2, sticky="w", padx=5, pady=(8,0))
        self.cb_status = ttk.Combobox(main_frame, values=self.list_status, state="readonly", font=("Segoe UI", 10))
        self.cb_status.set("Pendente")
        self.cb_status.grid(row=8, column=2, sticky="ew", padx=5, ipady=4) # ipady no combo ajusta altura

        # Linha de Configurações
        tk.Label(main_frame, text="CATEGORIA*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=9, column=0, sticky="w", padx=5, pady=(8,0))
        self.cb_cat = ttk.Combobox(main_frame, values=self.list_categorias, state="readonly", font=("Segoe UI", 10))
        self.cb_cat.grid(row=10, column=0, sticky="ew", padx=5, ipady=4)

        tk.Label(main_frame, text="FORMA", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=9, column=1, sticky="w", padx=5, pady=(8,0))
        self.cb_forma = ttk.Combobox(main_frame, values=self.list_formas, state="readonly", font=("Segoe UI", 10))
        self.cb_forma.set("Dinheiro")
        self.cb_forma.grid(row=10, column=1, sticky="ew", padx=5, ipady=4)

        tk.Label(main_frame, text="RECORRÊNCIA", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=9, column=2, sticky="w", padx=5, pady=(8,0))
        self.cb_recorrencia = ttk.Combobox(main_frame, values=self.list_recorrencia, state="readonly", font=("Segoe UI", 10))
        self.cb_recorrencia.set("Não Recorrente")
        self.cb_recorrencia.grid(row=10, column=2, sticky="ew", padx=5, ipady=4)

        # Painel de Parcelas
        self.frame_parcelas = tk.Frame(main_frame, bg="#E2E8F0", pady=8, padx=10)
        tk.Label(self.frame_parcelas, text="QTD PARCELAS:", bg="#E2E8F0", font=("Segoe UI", 8, "bold")).pack(side="left")
        self.ent_qtd_parc = tk.Entry(self.frame_parcelas, width=5, font=("Segoe UI", 10))
        self.ent_qtd_parc.pack(side="left", padx=5)
        self.ent_qtd_parc.insert(0, "1")
        self.lbl_calculo = tk.Label(self.frame_parcelas, text="= 1x R$ 0.00", bg="#E2E8F0", font=("Segoe UI", 9, "italic"), fg=self.cor_destaque)
        self.lbl_calculo.pack(side="left", padx=10)

        # Histórico
        tk.Label(main_frame, text="DETALHES DAS PARCELAS", bg=self.bg_fundo, fg=self.cor_destaque, font=("Segoe UI", 8, "bold")).grid(row=12, column=0, columnspan=3, sticky="w", pady=(20, 2), padx=5)
        self.tree_pagos = ttk.Treeview(main_frame, columns=("parc", "venc", "valor", "status"), show="headings", height=5, style="Hist.Treeview")
        for col, text in zip(("parc", "venc", "valor", "status"), ("Nº", "VENCIMENTO", "VALOR", "STATUS")):
            self.tree_pagos.heading(col, text=text)
            self.tree_pagos.column(col, anchor="center")
        self.tree_pagos.grid(row=13, column=0, columnspan=3, sticky="ew", padx=5)

        # Botões Finalização
        self.btn_salvar = tk.Button(main_frame, text="SALVAR DESPESA", bg=self.cor_btn_acao, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.validar_e_salvar)
        self.btn_salvar.grid(row=14, column=0, columnspan=3, pady=(20, 5), sticky="ew", ipady=8)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.destroy)
        self.btn_cancelar.grid(row=15, column=0, columnspan=3, pady=5, sticky="ew", ipady=8)

        # Efeitos Hover
        for btn in [self.btn_salvar, self.btn_cancelar]:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: self.btn_salvar.config(bg=self.cor_btn_acao))
        self.btn_cancelar.bind("<Leave>", lambda e: self.btn_cancelar.config(bg=self.cor_btn_sair))

    def validar_e_salvar(self):
        # Lógica de salvar...
        pass

    def preencher_dados(self, d):
        # Lógica de preencher...
        pass

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = JanelaCadastroDespesas(root)
    root.mainloop()