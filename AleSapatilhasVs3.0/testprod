import tkinter as tk
from tkinter import messagebox, ttk
import database 

class JanelaCadastroProdutos(tk.Toplevel):
    def __init__(self, master, dados_produto=None):
        super().__init__(master)
        
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

        # Configurações de Janela
        self.title("Alê Sapatilhas - Cadastro de Produtos")
        self.geometry("450x750") 
        self.resizable(False, False)
        self.configure(bg=self.bg_fundo)

        # ID para Edição
        self.produto_id = dados_produto[0] if dados_produto else None
        
        # Listas de Opções
        self.list_categorias = ["Sapatilhas", "Rasteiras", "Botas", "Mules", "Tênis", "Roupas"]
        self.list_materiais = ["Verniz", "Napa", "Nobuck", "Couro", "PU", "Algodão", "Suplex"]
        self.list_tamanhos = [str(i) for i in range(33, 41)] + ["P", "M", "G", "GG", "U"]
        self.list_cores = ["Preto", "Nude", "Branco", "Caramelo", "Rosa", "Azul", "Vermelho"]

        self.criar_widgets()
        
        if dados_produto:
            self.preencher_dados(dados_produto)
     
        self.grab_set()

    # --- FUNÇÕES DE COMPORTAMENTO (HOVER/FOCUS) ---
    def aplicar_estilo_input(self, widget):
        def ao_focar(e):
            widget.config(highlightbackground=self.cor_destaque, highlightthickness=2)
        def ao_perder_foco(e):
            widget.config(highlightbackground=self.cor_borda, highlightthickness=1)
        def ao_entrar(e):
            if widget != self.focus_get(): widget.config(highlightbackground="#94A3B8")
        def ao_sair(e):
            if widget != self.focus_get(): widget.config(highlightbackground=self.cor_borda)

        widget.bind("<FocusIn>", ao_focar)
        widget.bind("<FocusOut>", ao_perder_foco)
        widget.bind("<Enter>", ao_entrar)
        widget.bind("<Leave>", ao_sair)

    def aplicar_estilo_botao(self, botao, cor_original):
        botao.bind("<Enter>", lambda e: botao.config(bg=self.cor_hover_btn))
        botao.bind("<Leave>", lambda e: botao.config(bg=cor_original))

    def criar_widgets(self):
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=25, pady=20)
        main_frame.pack(fill="both", expand=True)

        # --- HEADER ---
        codigo = f"CÓDIGO: {self.produto_id}" if self.produto_id else "NOVO PRODUTO"
        tk.Label(main_frame, text=codigo, bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(main_frame, text="Gerenciar Estoque", bg=self.bg_fundo, fg=self.cor_texto, font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(0, 20))

        # --- CAMPOS GERAIS ---
        self.ent_produto = self.criar_campo_label(main_frame, "DESCRIÇÃO DO MODELO*")
        
        # Linha Categoria e Material
        frame_cat_mat = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_cat_mat.pack(fill="x", pady=5)
        
        self.var_cat = self.criar_option_label(frame_cat_mat, "CATEGORIA*", self.list_categorias, side="left")
        self.var_mat = self.criar_option_label(frame_cat_mat, "MATERIAL", self.list_materiais, side="right")

        # --- PREÇOS E MARKUP ---
        frame_precos = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_precos.pack(fill="x", pady=5)

        tk.Label(frame_precos, text="PREÇO CUSTO*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.ent_custo = tk.Entry(frame_precos, font=("Segoe UI", 11), bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_custo.grid(row=1, column=0, sticky="ew", ipady=5, padx=(0, 10))
        self.ent_custo.bind("<KeyRelease>", self.calcular_markup)
        self.aplicar_estilo_input(self.ent_custo)

        tk.Label(frame_precos, text="VENDA (MARKUP 2.4)", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w")
        self.ent_venda = tk.Entry(frame_precos, font=("Segoe UI", 11, "bold"), bg="#F1F5F9", fg=self.cor_destaque, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_venda.grid(row=1, column=1, sticky="ew", ipady=5)
        
        frame_precos.columnconfigure(0, weight=1)
        frame_precos.columnconfigure(1, weight=1)

        # --- QUANTIDADE TOTAL (CONFERÊNCIA) ---
        self.ent_qtd_total = self.criar_campo_label(main_frame, "QUANTIDADE TOTAL DO PEDIDO*")
        self.ent_qtd_total.config(font=("Segoe UI", 12, "bold"), fg=self.cor_destaque)

        # --- GRADE ---
        tk.Label(main_frame, text="DISTRIBUIÇÃO DA GRADE", bg=self.bg_fundo, fg=self.cor_texto, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(20, 5))
        
        frame_grade = tk.Frame(main_frame, bg=self.bg_card, bd=1, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, padx=15, pady=15)
        frame_grade.pack(fill="x")

        # Cor, Tamanho e Quantidade na Grade
        self.var_cor = self.criar_option_label(frame_grade, "COR*", self.list_cores)
        self.var_tam = self.criar_option_label(frame_grade, "TAMANHO*", self.list_tamanhos)
        
        tk.Label(frame_grade, text="QUANTIDADE NESTA VARIAÇÃO*", bg=self.bg_card, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10,0))
        self.ent_qtd_grade = tk.Entry(frame_grade, font=("Segoe UI", 11), bg=self.bg_fundo, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_qtd_grade.pack(fill="x", ipady=4)
        self.aplicar_estilo_input(self.ent_qtd_grade)

        # --- BOTÕES ---
        self.btn_salvar = tk.Button(main_frame, text="SALVAR PRODUTO", bg=self.cor_btn_acao, fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=self.validar_e_salvar)
        self.btn_salvar.pack(fill="x", pady=(30, 5), ipady=8)
        self.aplicar_estilo_botao(self.btn_salvar, self.cor_btn_acao)

        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.destroy)
        self.btn_cancelar.pack(fill="x", ipady=8)
        self.aplicar_estilo_botao(self.btn_cancelar, self.cor_btn_sair)

    # --- HELPERS DE INTERFACE ---
    def criar_campo_label(self, parent, texto):
        tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 0))
        ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        ent.pack(fill="x", ipady=5)
        self.aplicar_estilo_input(ent)
        return ent

    def criar_option_label(self, parent, texto, lista, side=None):
        frame = tk.Frame(parent, bg=parent["bg"])
        if side: frame.pack(side=side, fill="x", expand=True)
        else: frame.pack(fill="x")
        
        tk.Label(frame, text=texto, bg=frame["bg"], fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        var = tk.StringVar(value=lista[0])
        opt = tk.OptionMenu(frame, var, *lista)
        opt.config(bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, font=("Segoe UI", 9), cursor="hand2")
        opt.pack(fill="x", pady=(2, 5), padx=(0, 5) if side == "left" else 0)
        return var

    # --- LÓGICA ---
    def calcular_markup(self, event=None):
        try:
            custo = float(self.ent_custo.get().replace(",", "."))
            venda = custo * 2.4
            self.ent_venda.delete(0, tk.END)
            self.ent_venda.insert(0, f"{venda:.2f}")
        except ValueError:
            self.ent_venda.delete(0, tk.END)

    def validar_e_salvar(self):
        try:
            total_pedido = int(self.ent_qtd_total.get())
            total_grade = int(self.ent_qtd_grade.get())

            if total_pedido != total_grade:
                messagebox.showerror("Erro de Conferência", f"A quantidade da grade ({total_grade}) não bate com o total do pedido ({total_pedido})!")
                return

            d = {
                "produto": self.ent_produto.get().strip(),
                "cor": self.var_cor.get(),
                "tam": self.var_tam.get(),
                "custo": self.ent_custo.get().replace(",", "."),
                "venda": self.ent_venda.get(),
                "qtd": total_grade,
                "cat": self.var_cat.get(),
                "mat": self.var_mat.get(),
                "forn": "Diversos" # Padronizado
            }

            if not d["produto"] or not d["custo"]:
                messagebox.showwarning("Atenção", "Preencha os campos obrigatórios.")
                return

            database.salvar_item(d["produto"], d["cor"], d["tam"], d["custo"], d["venda"], d["qtd"], d["cat"], d["forn"], "Disponível")
            messagebox.showinfo("Sucesso", "Produto registrado com Markup e Grade conferida!")
            self.destroy()

        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores de preço e quantidade são numéricos.")

    def preencher_dados(self, d):
        self.ent_produto.insert(0, d[1])
        self.var_cor.set(d[2])
        self.var_tam.set(d[3])
        self.ent_custo.insert(0, d[4])
        self.calcular_markup()
        self.ent_qtd_total.insert(0, d[6])
        self.ent_qtd_grade.insert(0, d[6])
        self.var_cat.set(d[7])

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    JanelaCadastroProdutos(root)   
    root.mainloop()