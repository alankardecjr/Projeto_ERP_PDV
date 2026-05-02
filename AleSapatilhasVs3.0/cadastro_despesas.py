import tkinter as tk
from tkinter import messagebox
import database 

class JanelaCadastroDespesas(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        # --- PALETA DE CORES ---
        self.bg_fundo = "#f4f5f9"
        self.bg_card = "#ffffff"
        self.cor_borda = "#d1d5db"
        self.cor_texto = "#1f2937"
        self.cor_lbl = "#4b5563"
        self.cor_btn_salvar = "#4b5563" 
        self.cor_btn_cancelar = "#1f2937" 
        self.cor_hover_field = "#3b82f6" 
        self.cor_hover_btn = "#6b7280"

        self.title("Alê Sapatilhas - Lançamento de Despesas")
        self.geometry("450x750")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)

        self.criar_widgets()
        self.grab_set() # Foca a atenção nesta janela

    def criar_widgets(self):
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=25, pady=20)
        main_frame.pack(fill="both", expand=True)

        # --- AUXILIARES DE ESTILO ---
        def ao_entrar_botao(e, cor): e.widget.config(bg=cor)
        def ao_sair_botao(e, cor): e.widget.config(bg=cor)

        def criar_campo(parent, texto, row, col=0, colspan=2):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(10, 0))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                           relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=5)
            
            ent.bind("<FocusIn>", lambda e: e.widget.config(highlightbackground=self.cor_hover_field, highlightthickness=2))
            ent.bind("<FocusOut>", lambda e: e.widget.config(highlightbackground=self.cor_borda, highlightthickness=1))
            return ent

        # --- HEADER ---
        tk.Label(main_frame, text="Nova Despesa", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # --- FORMULÁRIO ---
        self.ent_desc = criar_campo(main_frame, "DESCRIÇÃO", 1)
        
        self.ent_valor = criar_campo(main_frame, "VALOR (R$)", 3)
        self.ent_valor.insert(0, "0.00")

        # --- TIPO DE DESPESA (Check constraint no banco: 'Fixo' ou 'Adicional') ---
        tk.Label(main_frame, text="TIPO DE GASTO", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=5, column=0, sticky="w", pady=(15, 0))
        
        self.var_tipo = tk.StringVar(value="Fixo")
        frame_radio = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_radio.grid(row=6, column=0, columnspan=2, sticky="w")
        
        tk.Radiobutton(frame_radio, text="Fixo (Mensal)", variable=self.var_tipo, value="Fixo", 
                       bg=self.bg_fundo, font=("Segoe UI", 9)).pack(side="left", padx=(0, 15))
        tk.Radiobutton(frame_radio, text="Adicional / Compra", variable=self.var_tipo, value="Adicional", 
                       bg=self.bg_fundo, font=("Segoe UI", 9)).pack(side="left")

        # --- CATEGORIA ---
        tk.Label(main_frame, text="CATEGORIA", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=7, column=0, sticky="w", pady=(15, 0))
        
        self.var_cat = tk.StringVar(value="Infraestrutura")
        categorias = ["Infraestrutura", "Compra de Mercadoria", "Marketing", "Salários", "Impostos", "Outros"]
        self.opt_cat = tk.OptionMenu(main_frame, self.var_cat, *categorias)
        self.opt_cat.config(bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, cursor="hand2")
        self.opt_cat.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # --- BOTÕES ---
        self.btn_salvar = tk.Button(main_frame, text="CONFIRMAR LANÇAMENTO", bg=self.cor_btn_salvar, fg="white", 
                                    font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", 
                                    command=self.salvar_despesa)
        self.btn_salvar.grid(row=9, column=0, columnspan=2, pady=(30, 0), sticky="ew", ipady=8)
        self.btn_salvar.bind("<Enter>", lambda e: ao_entrar_botao(e, self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: ao_sair_botao(e, self.cor_btn_salvar))

        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_cancelar, fg="white", 
                                       font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", 
                                       command=self.destroy)
        self.btn_cancelar.grid(row=10, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=5)
        self.btn_cancelar.bind("<Enter>", lambda e: ao_entrar_botao(e, "#374151"))
        self.btn_cancelar.bind("<Leave>", lambda e: ao_sair_botao(e, self.cor_btn_cancelar))

        main_frame.columnconfigure(0, weight=1)

    def salvar_despesa(self):
        desc = self.ent_desc.get().strip()
        valor_raw = self.ent_valor.get().replace(",", ".").strip()
        tipo = self.var_tipo.get()
        cat = self.var_cat.get()

        if not desc or not valor_raw:
            messagebox.showwarning("Atenção", "Preencha a descrição e o valor.")
            return

        try:
            valor = float(valor_raw)
            # Chama a função do banco de dados (database.py)
            database.registrar_despesa(desc, valor, tipo, cat)
            
            messagebox.showinfo("Sucesso", f"Lançamento de {cat} registrado!")
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro", "O valor inserido é inválido. Use números (ex: 150.50)")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroDespesas(root)
    root.mainloop()