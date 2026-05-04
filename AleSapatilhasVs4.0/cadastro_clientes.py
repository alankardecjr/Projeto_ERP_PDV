import tkinter as tk
from tkinter import messagebox
import database 

class JanelaCadastroClientes(tk.Toplevel):
    def __init__(self, master, dados_cliente=None):
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
        
        self.title("Alê Sapatilhas - Gestão de Clientes")
        self.geometry("500x820")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)

        self.cliente_id = None
        self.criar_widgets()
        
        if dados_cliente:
            self.preencher_dados(dados_cliente)
     
        self.grab_set()

    def criar_widgets(self):
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        def criar_campo(parent, texto, row, col=0, colspan=2, width=None):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(6, 0))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                            relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            
            if width: ent.config(width=width)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=3, padx=(0, 5) if colspan==1 else 0)
            
            # --- LÓGICA DE HOVER E FOCUS (DESTAQUE) ---
            def on_enter(e):
                if self.focus_get() != ent:
                    ent.config(highlightbackground=self.cor_hover_field, highlightthickness=1)

            def on_leave(e):
                if self.focus_get() != ent:
                    ent.config(highlightbackground=self.cor_borda, highlightthickness=1)

            def on_focus_in(e):
                ent.config(highlightbackground=self.cor_destaque, highlightthickness=2)

            def on_focus_out(e):
                ent.config(highlightbackground=self.cor_borda, highlightthickness=1)

            ent.bind("<Enter>", on_enter)
            ent.bind("<Leave>", on_leave)
            ent.bind("<FocusIn>", on_focus_in)
            ent.bind("<FocusOut>", on_focus_out)
            
            return ent

        # Título
        tk.Label(main_frame, text="Ficha Cadastral do Cliente", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Campos de Entrada
        self.ent_nome   = criar_campo(main_frame, "NOME COMPLETO*", 1)
        self.ent_cpf    = criar_campo(main_frame, "CPF (APENAS NÚMEROS)*", 3)
        self.ent_tel    = criar_campo(main_frame, "TELEFONE / WHATSAPP*", 5, col=0, colspan=1)
        self.ent_email  = criar_campo(main_frame, "E-MAIL", 5, col=1, colspan=1)
        self.ent_niver  = criar_campo(main_frame, "ANIVERSÁRIO (DD/MM)", 7, col=0, colspan=1)
        self.ent_tam    = criar_campo(main_frame, "TAM. CALÇADO", 7, col=1, colspan=1)
        self.ent_logra  = criar_campo(main_frame, "ENDEREÇO COMPLETO", 9)
        self.ent_bairro = criar_campo(main_frame, "BAIRRO", 11, col=0, colspan=1)
        self.ent_cidade = criar_campo(main_frame, "CIDADE", 11, col=1, colspan=1)
        self.ent_cep    = criar_campo(main_frame, "CEP", 13, col=0, colspan=1)       
        self.ent_limite = criar_campo(main_frame, "LIMITE DE CRÉDITO", 13, col=1, colspan=1)
        self.ent_limite.insert(0, "0.00")

        self.ent_obs = criar_campo(main_frame, "OBSERVAÇÕES", 15)

        # Seleção de Status
        tk.Label(main_frame, text="CLASSIFICAÇÃO", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=17, column=0, sticky="w", pady=(10, 0))
        
        self.var_status = tk.StringVar(value="Ativo")
        self.opt_status = tk.OptionMenu(main_frame, self.var_status, "Vip", "Ativo", "Inativo", "Bloqueado")
        self.opt_status.config(bg=self.bg_card, fg=self.cor_texto, relief="flat", highlightthickness=1, 
                                highlightbackground=self.cor_borda, font=("Segoe UI", 10), cursor="hand2")
        self.opt_status["menu"].config(bg=self.bg_card, fg=self.cor_texto)
        self.opt_status.grid(row=18, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # Botão Salvar (Inicia como cadastro novo)
        self.btn_salvar = tk.Button(main_frame, text="SALVAR CLIENTE", bg=self.cor_btn_acao, fg="white", 
                                    font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                    command=self.salvar_dados)
        self.btn_salvar.grid(row=19, column=0, columnspan=2, pady=(30, 0), sticky="ew", ipady=8)
        
        # Botão Cancelar
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", 
                                      font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", 
                                      command=self.destroy)
        self.btn_cancelar.grid(row=20, column=0, columnspan=2, pady=(10, 0), sticky="ew", ipady=8)

        # --- BINDING DE EFEITOS NOS BOTÕES ---
        def configurar_hovers():
            # A cor original do botão salvar muda se for edição
            cor_atual_salvar = self.btn_salvar.cget("bg")
            self.btn_salvar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
            self.btn_salvar.bind("<Leave>", lambda e: e.widget.config(bg=cor_atual_salvar))
            
            self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_destaque))
            self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        configurar_hovers()
        self.configurar_hovers = configurar_hovers # Referência para atualizar após preencher dados

        # Expansão das colunas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def salvar_dados(self):
        d = {
            "nome": self.ent_nome.get().strip(),
            "cpf": self.ent_cpf.get().strip(),
            "tel": self.ent_tel.get().strip(),
            "email": self.ent_email.get().strip(),
            "niver": self.ent_niver.get().strip(),
            "tam": self.ent_tam.get().strip() or 0,
            "endereco": self.ent_logra.get().strip(),
            "bairro": self.ent_bairro.get().strip(),
            "cidade": self.ent_cidade.get().strip(),
            "cep": self.ent_cep.get().strip(),
            "obs": self.ent_obs.get().strip(),
            "limite": self.ent_limite.get().strip() or 0,
            "status": self.var_status.get()
        }
        
        if not d["nome"] or not d["cpf"] or not d["tel"]:
            messagebox.showwarning("Atenção", "Preencha Nome, CPF e Telefone obrigatoriamente.")
            return

        try:
            if self.cliente_id:
                database.atualizar_cliente(
                    self.cliente_id, 
                    nome=d["nome"], cpf=d["cpf"], telefone=d["tel"], email=d["email"],
                    aniversario=d["niver"], tamanho_calcado=d["tam"], 
                    endereco_completo=d["endereco"], bairro=d["bairro"],
                    cidade=d["cidade"], cep=d["cep"], observacao=d["obs"],
                    limite_credito=d["limite"], status_cliente=d["status"]
                )
                messagebox.showinfo("Sucesso", "Cadastro atualizado!")
            else:
                database.cadastrar_cliente(
                    d["nome"], d["cpf"], d["tel"], d["email"],
                    d["niver"], d["tam"], d["endereco"], d["bairro"],
                    d["cidade"], d["cep"], d["obs"], d["limite"]
                )
                messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def preencher_dados(self, d):
        self.cliente_id = d[0]
        self.ent_nome.insert(0, d[1])
        self.ent_cpf.insert(0, d[2] if d[2] else "")
        self.ent_tel.insert(0, d[3])
        self.ent_email.insert(0, d[4] if d[4] else "")
        self.ent_niver.insert(0, d[5] if d[5] else "")
        self.ent_tam.insert(0, d[6] if d[6] else "")
        self.ent_logra.insert(0, d[7] if d[7] else "")
        self.ent_bairro.insert(0, d[8] if d[8] else "")
        self.ent_cidade.insert(0, d[9] if d[9] else "")
        self.ent_cep.insert(0, d[10] if d[10] else "")
        self.ent_obs.insert(0, d[11] if d[11] else "")
        self.ent_limite.delete(0, "end")
        self.ent_limite.insert(0, d[12])
        self.var_status.set(d[14])
        
        # Ajuste visual para modo edição
        self.btn_salvar.config(text="ATUALIZAR CADASTRO",bg=self.cor_btn_acao, fg="white")
        self.configurar_hovers() 
        
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    JanelaCadastroClientes(root)
    root.mainloop()