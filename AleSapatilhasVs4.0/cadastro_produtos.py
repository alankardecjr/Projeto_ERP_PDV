import tkinter as tk
from tkinter import messagebox, ttk
import database 

class JanelaCadastroProdutos(tk.Toplevel):
    def __init__(self, master, dados_produto=None):
        super().__init__(master)
        
        # --- PALETA DE CORES ---
        self.bg_fundo       = "#F1F5F9"
        self.bg_card        = "#FFFFFF"
        self.cor_borda      = "#8BA2BD"
        self.cor_texto      = "#0B1933"
        self.cor_lbl        = "#020C18"
        self.cor_destaque   = "#6366F1" 
        self.cor_btn_menu   = "#1E293B"
        self.cor_btn_sair   = "#25324E"
        self.cor_btn_acao   = "#425074" 
        self.cor_hover_btn  = "#5B7FB5"
        self.cor_hover_field = "#484AD6" 

        self.title("Alê Sapatilhas - Gestão de Estoque")
        self.geometry("500x820") 
        self.resizable(False, False)
        self.configure(bg=self.bg_fundo)

        self.produto_id = dados_produto[0] if dados_produto else None
        
        # Listas para os Comboboxes
        self.list_categorias = ["Biquinis", "Botas", "Mules", "Rasteiras", "Roupas", "Salto Block", "Salto Fino", "Sapatilhas", "Tênis"]     
        self.list_materiais = ["Algodão", "Couro", "Napa", "Nobuck", "Poliamida", "PU", "Suplex", "Verniz"]      
        self.list_tamanhos = [str(i) for i in range(33, 41)] + ["P", "M", "G", "GG", "U"]        
        self.list_cores = ["Amarelo", "Azul", "Branco", "Caramelo", "Nude", "Off", "Outros", "Preto", "Rosa", "Verde", "Vermelho"]

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

    def criar_widgets(self):
        # 1. Container Principal (Igual ao Cliente)
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 2. Função Interna criar_campo (Padronizada)
        def criar_campo(parent, texto, row, col=0, colspan=2, width=None):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(6, 0))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                            relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            
            if width: ent.config(width=width)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=3, padx=(0, 5) if colspan==1 else 0)
            
            # Efeitos de Foco e Hover
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
            return ent

        # 3. Função Interna criar_combo (Para manter o padrão nos menus de rolagem)
        def criar_combo(parent, texto, lista, row, col, span=1):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(6, 0))
            combo = ttk.Combobox(parent, values=lista, font=("Segoe UI", 10), state="readonly")
            combo.set(lista[0])
            combo.grid(row=row+1, column=col, columnspan=span, sticky="ew", padx=(0, 5) if col==0 else 0)
            return combo

        # --- TITULO ---
        tk.Label(main_frame, text="Ficha Técnica do Produto", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # --- CAMPOS DE ENTRADA ---
        self.ent_produto = criar_campo(main_frame, "DESCRIÇÃO DO MODELO*", 1)
        
        self.cb_cat = criar_combo(main_frame, "CATEGORIA*", self.list_categorias, 3, 0)
        self.cb_mat = criar_combo(main_frame, "MATERIAL", self.list_materiais, 3, 1)

        # Preços (Custo e Venda lado a lado)
        tk.Label(main_frame, text="PREÇO CUSTO*", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=5, column=0, sticky="w", pady=(6,0))
        self.ent_custo = tk.Entry(main_frame, font=("Segoe UI", 11), bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_custo.grid(row=6, column=0, sticky="ew", ipady=3, padx=(0, 5))
        self.ent_custo.bind("<KeyRelease>", self.calcular_markup)
        
        tk.Label(main_frame, text="VENDA (MARKUP 2.4)", bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).grid(row=5, column=1, sticky="w", pady=(6,0))
        self.ent_venda = tk.Entry(main_frame, font=("Segoe UI", 11, "bold"), bg="#E2E8F0", fg=self.cor_destaque, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_venda.grid(row=6, column=1, sticky="ew", ipady=3)

        self.ent_forn = criar_campo(main_frame, "FORNECEDOR*", 7)

        # --- DISTRIBUIÇÃO DA GRADE ---
        tk.Label(main_frame, text="DISTRIBUIÇÃO DA GRADE", bg=self.bg_fundo, fg=self.cor_texto, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(20, 5))
        
        frame_grade = tk.Frame(main_frame, bg=self.bg_card, bd=0, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, padx=15, pady=15)
        frame_grade.pack(fill="x")

        self.var_cor = self.criar_option_label(frame_grade, "COR*", self.list_cores)
        self.var_tam = self.criar_option_label(frame_grade, "TAMANHO*", self.list_tamanhos)
        
        tk.Label(frame_grade, text="QUANTIDADE*", bg=self.bg_card, fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10,0))
        self.ent_qtd_grade = tk.Entry(frame_grade, font=("Segoe UI", 11), bg=self.bg_fundo, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_qtd_grade.pack(fill="x", ipady=4)
        self.aplicar_estilo_input(self.ent_qtd_grade)

        # --- BOTÕES ---
        texto_botao = "ATUALIZAR PRODUTO" if self.produto_id else "SALVAR PRODUTO"
        cor_base = self.cor_destaque if self.produto_id else self.cor_btn_acao

        self.btn_salvar = tk.Button(main_frame, text=texto_botao, bg=cor_base, fg="white", 
                                    font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                    command=self.validar_e_salvar)
        self.btn_salvar.grid(row=11, column=0, columnspan=2, pady=(30, 0), sticky="ew", ipady=8)
        
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", 
                                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                      command=self.destroy)
        self.btn_cancelar.grid(row=12, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=8)

        # --- CONFIGURAR HOVERS ---
        def configurar_hovers():
            cor_atual_salvar = self.btn_salvar.cget("bg")
            self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
            self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=cor_atual_salvar))
            
            self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_destaque))
            self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        configurar_hovers()
        self.configurar_hovers = configurar_hovers

    # --- CÁLCULO DE MARKUP ---
    def calcular_markup(self, event=None):
        try:
            custo_str = self.ent_custo.get().replace(",", ".")
            if custo_str:
                custo = float(custo_str)
                venda = custo * 2.4
                self.ent_venda.delete(0, tk.END)
                self.ent_venda.insert(0, f"{venda:.2f}")
        except ValueError:
            self.ent_venda.delete(0, tk.END)

    # --- VALIDAÇÃO E SALVAMENTO (COMUNICANDO COM O DATABASE) ---

    def validar_e_salvar(self):
        try:
            d = {
                "produto": self.ent_produto.get().strip(),
                "cor": self.var_cor.get(),
                "tam": self.var_tam.get(),
                "custo": self.ent_custo.get().replace(",", "."),
                "venda": self.ent_venda.get().replace(",", "."),
                "qtd": self.ent_qtd_grade.get().strip(),
                "cat": self.var_cat.get(),
                "mat": self.var_mat.get(),
                "forn": self.ent_forn.get().strip()
            }

            if not d["produto"] or not d["custo"] or not d["qtd"] or not d["forn"]:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios (*).")
                return

            if self.produto_id:
                database.atualizar_produto(
                    self.produto_id, sku=None, produto=d["produto"], marca=d["mat"], 
                    cor=d["cor"], tamanho=d["tam"], precocusto=d["custo"], 
                    precovenda=d["venda"], quantidade=d["qtd"], categoria=d["cat"], fornecedor=d["forn"]
                )
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            else:
                database.cadastrar_produto(
                    None, d["produto"], d["mat"], d["cor"], d["tam"], 
                    d["custo"], d["venda"], d["qtd"], d["cat"], d["forn"]
                )
                messagebox.showinfo("Sucesso", "Novo produto cadastrado!")
            
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar: {e}")

    def preencher_dados(self, d):
        # d: (id, sku, produto, marca/material, cor, tamanho, custo, venda, qtd, cat, forn, status)
        self.ent_produto.insert(0, d[2])
        self.var_mat.set(d[3] if d[3] in self.list_materiais else self.list_materiais[0])
        self.var_cor.set(d[4])
        self.var_tam.set(str(d[5]))
        self.ent_custo.insert(0, f"{d[6]:.2f}")
        self.ent_venda.insert(0, f"{d[7]:.2f}")
        self.ent_qtd_grade.insert(0, d[8])
        self.var_cat.set(d[9])
        self.ent_forn.insert(0, d[10] if d[10] else "")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    JanelaCadastroProdutos(root)   
    root.mainloop()