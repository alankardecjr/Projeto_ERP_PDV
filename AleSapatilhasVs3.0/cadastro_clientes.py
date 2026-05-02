import tkinter as tk
from tkinter import messagebox
import sqlite3
import database 

class JanelaCadastroClientes(tk.Toplevel):
    def __init__(self, master, dados_cliente=None, callback_venda=None):
        super().__init__(master)

        # --- PALETA DE CORES ---
        self.bg_fundo = "#f4f5f9"
        self.bg_card = "#ffffff"
        self.cor_borda = "#d1d5db"
        self.cor_texto = "#161f29"
        self.cor_lbl = "#121a26"
        self.cor_btn_1 = "#4b5563"   
        self.cor_btn_2 = "#374151"   
        self.cor_btn_sair = "#1f2937" 
        self.cor_hover_field = "#3b82f6"   
        self.cor_hover_btn = "#6b7280"

        self.title("Alê Sapatilhas - Cadastro de Clientes")
        self.geometry("450x750")
        self.configure(bg=self.bg_fundo)
        self.resizable(False, False)

        #Dados do cliente: (id, nome, tel, niver, tam, logra, num, bairro, cidade, ref, obs, status)
        self.cliente_id = None
        self.callback_venda = callback_venda 
        self.criar_widgets()
        
        # Se dados do cliente forem passados, preenche os campos para edição
        if dados_cliente:
            self.preencher_dados(dados_cliente)            
     
        self.grab_set()

    def criar_widgets(self):
        # Reduzi o pady do main_frame para economizar espaço
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)

        def ao_entrar_botao(e, cor_destaque):
            e.widget.config(bg=cor_destaque)

        def ao_sair_botao(e, cor_original):
            e.widget.config(bg=cor_original)

        def criar_campo(parent, texto, row, col=0, colspan=2, width=None):
            tk.Label(parent, text=texto, bg=self.bg_fundo, fg=self.cor_lbl, 
                     font=("Segoe UI", 8, "bold")).grid(row=row, column=col, sticky="w", pady=(6, 0))
            
            ent = tk.Entry(parent, font=("Segoe UI", 10), bg=self.bg_card, fg=self.cor_texto,
                            relief="flat", highlightbackground=self.cor_borda, highlightthickness=1)
            
            if width: ent.config(width=width)
            ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", ipady=3, padx=(0, 5) if colspan==1 else 0)
            
            # --- EFEITO HOVER E FOCUS NO INPUT ---
            def on_enter(e):
                if e.widget != self.focus_get():
                    e.widget.config(highlightbackground="#9ca3af") # Cinza mais escuro no hover

            def on_leave(e):
                if e.widget != self.focus_get():
                    e.widget.config(highlightbackground=self.cor_borda)

            def on_focus_in(e):
                e.widget.config(highlightbackground=self.cor_hover_field, highlightthickness=2)

            def on_focus_out(e):
                e.widget.config(highlightbackground=self.cor_borda, highlightthickness=1)

            ent.bind("<Enter>", on_enter)
            ent.bind("<Leave>", on_leave)
            ent.bind("<FocusIn>", on_focus_in)
            ent.bind("<FocusOut>", on_focus_out)
            
            return ent

        # --- HEADER ---
        lbl_header = tk.Label(main_frame, text="Gerenciar Cliente", bg=self.bg_fundo, 
                               fg=self.cor_texto, font=("Segoe UI", 14, "bold"))
        lbl_header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        # --- CAMPOS COMPACTADOS ---
        self.ent_nome = criar_campo(main_frame, "NOME COMPLETO*", 1)
        self.ent_tel = criar_campo(main_frame, "TELEFONE / WHATSAPP*", 3) 

        # Linha dupla: Aniversário e Tamanho do Pé
        self.ent_niver = criar_campo(main_frame, "ANIVERSÁRIO (DD/MM)", 5, col=0, colspan=1)
        self.ent_tam = criar_campo(main_frame, "TAM. PÉ", 5, col=1, colspan=1)
     
        # Linha dupla: Logradouro e Número 
        self.ent_logra = criar_campo(main_frame, "LOGRADOURO", 7, col=0, colspan=1)
        self.ent_num = criar_campo(main_frame, "Nº", 7, col=1, colspan=1)

        # Linha dupla: Bairro e Cidade        
        self.ent_bairro = criar_campo(main_frame, "BAIRRO", 9, col=0, colspan=1)
        self.ent_cidade = criar_campo(main_frame, "CIDADE", 9, col=1, colspan=1)    

        # Campo de Referência com largura maior para acomodar descrições mais longas
        self.ent_ref = criar_campo(main_frame, "REFERÊNCIA", 11)

        # Dica: Definir uma largura fixa para os campos não "esticarem" demais
        self.ent_niver.config(width=15)
        self.ent_tam.config(width=10)
        
        # Observação como Entry simples em vez de Text para salvar espaço vertical
        self.ent_obs = criar_campo(main_frame, "OBSERVAÇÕES", 13)

        # --- STATUS ---
        tk.Label(main_frame, text="STATUS", bg=self.bg_fundo, fg=self.cor_lbl, 
                 font=("Segoe UI", 8, "bold")).grid(row=15, column=0, sticky="w", pady=(8, 0))
        
        self.var_status = tk.StringVar(value="Ativo")
        self.opt_status = tk.OptionMenu(main_frame, self.var_status, "Ativo", "Inativo", "Fidelidade", "Revenda")
        self.opt_status.config(bg=self.bg_card, fg=self.cor_texto, relief="flat", highlightthickness=1, 
                                highlightbackground=self.cor_borda, font=("Segoe UI", 9), cursor="hand2")
        self.opt_status.grid(row=16, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        # --- BOTÕES ---
        btn_frame = tk.Frame(main_frame, bg=self.bg_fundo)
        btn_frame.grid(row=17, column=0, columnspan=2, pady=(20, 5))

        self.btn_salvar = tk.Button(btn_frame, text="SALVAR DADOS", bg=self.cor_btn_1, fg="white", 
                                    font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2", 
                                    command=self.salvar_e_sair)
        self.btn_salvar.pack(side="left", padx=5, ipady=6)
        self.btn_salvar.bind("<Enter>", lambda e: ao_entrar_botao(e, self.cor_hover_btn))
        self.btn_salvar.bind("<Leave>", lambda e: ao_sair_botao(e, self.cor_btn_1))

        self.btn_venda = tk.Button(btn_frame, text="GERAR VENDA", bg=self.cor_btn_2, fg="white", 
                                    font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2", 
                                    command=self.salvar_e_vender)
        self.btn_venda.pack(side="left", padx=5, ipady=6)
        self.btn_venda.bind("<Enter>", lambda e: ao_entrar_botao(e, "#4b5563"))
        self.btn_venda.bind("<Leave>", lambda e: ao_sair_botao(e, self.cor_btn_2))

        # Botão Cancelar agora com maior destaque visual no fundo
        self.btn_cancelar = tk.Button(main_frame, text="CANCELAR", bg=self.cor_btn_sair, fg="white", 
                                        font=("Segoe UI", 9, "bold"), width=32, relief="flat", cursor="hand2", 
                                        command=self.fechar_limpar)
        self.btn_cancelar.grid(row=18, column=0, columnspan=2, pady=(10, 0), ipady=5)
        self.btn_cancelar.bind("<Enter>", lambda e: ao_entrar_botao(e, "#374151"))
        self.btn_cancelar.bind("<Leave>", lambda e: ao_sair_botao(e, self.cor_btn_sair))

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def fechar_limpar(self):
        self.grab_release()
        self.destroy()

    def coletar_dados(self):
        return {
            "nome": self.ent_nome.get().strip(),
            "tel": self.ent_tel.get().strip(),
            "niver": self.ent_niver.get().strip(),
            "tam": self.ent_tam.get().strip(),
            "logra": self.ent_logra.get().strip(),
            "num": self.ent_num.get().strip(),
            "bairro": self.ent_bairro.get().strip(),
            "cidade": self.ent_cidade.get().strip(),
            "ref": self.ent_ref.get().strip(),
            "obs": self.ent_obs.get().strip(),
            "status": self.var_status.get()
        }

    def validar_e_salvar(self):
        d = self.coletar_dados()
        if not d["nome"] or not d["tel"]:
            messagebox.showwarning("Atenção", "Os campos NOME e TELEFONE devem ser preenchidos.")
            return False
        try:
            if self.cliente_id:
                # Aqui você pode chamar a função de update que criamos no database.py
                database.atualizar_status_cliente(self.cliente_id, d["status"])
            else:
                database.salvar_cliente(
                    d["nome"], d["tel"], d["niver"], d["tam"], d["logra"], 
                    d["num"], d["bairro"], d["cidade"], d["ref"], d["obs"], d["status"]
                )
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")
            return False

    def salvar_e_sair(self):
        if self.validar_e_salvar():
            self.fechar_limpar()

    def salvar_e_vender(self):
        d = self.coletar_dados()
        if self.validar_e_salvar():
            if self.callback_venda:
                self.callback_venda(d["nome"], d["tel"])
            self.fechar_limpar()

    def preencher_dados(self, d):
        self.cliente_id = d[0]
        self.ent_nome.insert(0, d[1])
        self.ent_tel.insert(0, d[2])
        self.ent_niver.insert(0, d[3])
        self.ent_tam.insert(0, d[4])
        self.ent_logra.insert(0, d[5])
        self.ent_num.insert(0, d[6])
        self.ent_bairro.insert(0, d[7])
        self.ent_cidade.insert(0, d[8])
        self.ent_ref.insert(0, d[9])
        self.ent_obs.insert(0, d[10])
        self.var_status.set(d[11])
        self.btn_salvar.config(text="ATUALIZAR")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    JanelaCadastroClientes(root)
    root.mainloop()