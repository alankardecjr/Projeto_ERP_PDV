import tkinter as tk
from tkinter import messagebox, ttk
import database
import ui_utils

class JanelaPagamento(tk.Toplevel):
    def __init__(self, master, cliente_selecionado, carrinho, total_venda):
        super().__init__(master)

        # --- Paleta de cores ---
        paleta = ui_utils.get_paleta()
        self.bg_fundo = paleta["bg_fundo"]
        self.bg_card = paleta["bg_card"]
        self.cor_borda = paleta["cor_borda"]
        self.cor_texto = paleta["cor_texto"]
        self.cor_lbl = paleta["cor_lbl"]
        self.cor_btn_acao = paleta["cor_btn_acao"]
        self.cor_btn_sair = paleta["cor_btn_sair"]
        self.cor_hover_btn = paleta["cor_hover_btn"]
        self.cor_destaque = paleta["cor_destaque"]

        self.title("Alê Sapatilhas - Gestão de Pagamento")
        self.configure(bg=self.bg_fundo)

        # --- Aplicar dimensões ---
        ui_utils.calcular_dimensoes_janela(self, largura_desejada=800, altura_desejada=600)

        self.cliente_selecionado = cliente_selecionado  # (id, nome, tel)
        self.carrinho = carrinho  # [(id, produto, qtd, preco, subtotal)]
        self.total_venda = total_venda

        self.setup_layout()
        self.grab_set()

    def setup_layout(self):
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # --- Título ---
        tk.Label(main_frame, text="💳 GESTÃO DE PAGAMENTO", bg=self.bg_fundo,
                 fg=self.cor_texto, font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        # --- Frame Cliente ---
        frame_cliente = tk.LabelFrame(main_frame, text="Cliente", bg=self.bg_card, fg=self.cor_texto,
                                      font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        frame_cliente.pack(fill="x", pady=(0, 10))

        tk.Label(frame_cliente, text=f"Nome: {self.cliente_selecionado[1]}", bg=self.bg_card,
                 fg=self.cor_texto, font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(frame_cliente, text=f"Telefone: {self.cliente_selecionado[2]}", bg=self.bg_card,
                 fg=self.cor_texto, font=("Segoe UI", 10)).pack(anchor="w")

        # --- Frame Itens ---
        frame_itens = tk.LabelFrame(main_frame, text="Itens da Venda", bg=self.bg_card, fg=self.cor_texto,
                                    font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        frame_itens.pack(fill="both", expand=True, pady=(0, 10))

        # Treeview para itens
        self.tree_itens = ttk.Treeview(frame_itens, columns=("Produto", "Qtd", "Preço", "Subtotal"), show="headings", height=8)
        for col in [("Produto", 200), ("Qtd", 60), ("Preço", 80), ("Subtotal", 80)]:
            self.tree_itens.heading(col[0], text=col[0])
            self.tree_itens.column(col[0], width=col[1], anchor="center")
        self.tree_itens.pack(fill="both", expand=True)

        # Preencher itens
        for item in self.carrinho:
            self.tree_itens.insert("", "end", values=(item[1], item[2], f"R$ {item[3]:.2f}", f"R$ {item[4]:.2f}"))

        # --- Frame Totais ---
        frame_totais = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_totais.pack(fill="x", pady=(0, 20))

        tk.Label(frame_totais, text=f"TOTAL: R$ {self.total_venda:.2f}", bg=self.bg_fundo,
                 fg=self.cor_destaque, font=("Segoe UI", 20, "bold")).pack(side="right")

        # --- Frame Pagamento ---
        frame_pagamento = tk.LabelFrame(main_frame, text="Forma de Pagamento", bg=self.bg_card, fg=self.cor_texto,
                                        font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        frame_pagamento.pack(fill="x", pady=(0, 20))

        # Forma de pagamento
        tk.Label(frame_pagamento, text="Forma de Pagamento:", bg=self.bg_card, fg=self.cor_lbl,
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.var_forma = tk.StringVar(value="Dinheiro")
        formas = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Pix", "Cheque"]
        self.cb_forma = ttk.Combobox(frame_pagamento, textvariable=self.var_forma, values=formas,
                                     state="readonly", font=("Segoe UI", 10))
        self.cb_forma.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Parcelas (só para cartão)
        tk.Label(frame_pagamento, text="Parcelas:", bg=self.bg_card, fg=self.cor_lbl,
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.var_parcelas = tk.StringVar(value="1")
        parcelas = ["1", "2", "3", "4", "5", "6"]
        self.cb_parcelas = ttk.Combobox(frame_pagamento, textvariable=self.var_parcelas, values=parcelas,
                                        state="readonly", font=("Segoe UI", 10))
        self.cb_parcelas.grid(row=1, column=1, sticky="ew")

        # Desconto
        tk.Label(frame_pagamento, text="Desconto (R$):", bg=self.bg_card, fg=self.cor_lbl,
                 font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))

        self.ent_desconto = tk.Entry(frame_pagamento, font=("Segoe UI", 10), bg="white", relief="flat",
                                     highlightthickness=1, highlightbackground=self.cor_borda)
        self.ent_desconto.grid(row=3, column=0, sticky="ew", padx=(0, 10))
        self.ent_desconto.insert(0, "0.00")

        # Valor final
        self.lbl_valor_final = tk.Label(frame_pagamento, text=f"Valor Final: R$ {self.total_venda:.2f}",
                                        bg=self.bg_card, fg=self.cor_destaque, font=("Segoe UI", 12, "bold"))
        self.lbl_valor_final.grid(row=3, column=1, sticky="e")

        # Bind para atualizar valor final quando desconto muda
        self.ent_desconto.bind("<KeyRelease>", self.atualizar_valor_final)
        self.cb_forma.bind("<<ComboboxSelected>>", self.atualizar_parcelas)

        # --- Botões ---
        frame_botoes = tk.Frame(main_frame, bg=self.bg_fundo)
        frame_botoes.pack(fill="x")

        self.btn_cancelar = tk.Button(frame_botoes, text="CANCELAR", bg=self.cor_btn_sair, fg="white",
                                      font=("Segoe UI", 10, "bold"), relief="flat", command=self.destroy)
        self.btn_cancelar.pack(side="left", padx=(0, 10), ipady=8, expand=True)

        self.btn_finalizar = tk.Button(frame_botoes, text="FINALIZAR VENDA", bg=self.cor_btn_acao, fg="white",
                                       font=("Segoe UI", 12, "bold"), relief="flat", command=self.finalizar_venda)
        self.btn_finalizar.pack(side="right", ipady=8, expand=True)

        # Hover effects
        self.btn_cancelar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_cancelar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_sair))

        self.btn_finalizar.bind("<Enter>", lambda e: e.widget.config(bg=self.cor_hover_btn))
        self.btn_finalizar.bind("<Leave>", lambda e: e.widget.config(bg=self.cor_btn_acao))

    def atualizar_parcelas(self, event=None):
        """Habilita/desabilita parcelas baseado na forma de pagamento"""
        if self.var_forma.get() == "Cartão de Crédito" or self.var_forma.get() == "Cartão de Débito":
            self.cb_parcelas.config(state="readonly")
        else:
            self.var_parcelas.set("1")
            self.cb_parcelas.config(state="disabled")

    def atualizar_valor_final(self, event=None):
        """Atualiza o valor final com desconto"""
        try:
            desconto = float(self.ent_desconto.get() or 0)
            valor_final = max(0, self.total_venda - desconto)
            self.lbl_valor_final.config(text=f"Valor Final: R$ {valor_final:.2f}")
        except ValueError:
            self.lbl_valor_final.config(text=f"Valor Final: R$ {self.total_venda:.2f}")

    def finalizar_venda(self):
        """Processa a finalização da venda"""
        try:
            desconto = float(self.ent_desconto.get() or 0)
            valor_final = max(0, self.total_venda - desconto)

            if valor_final <= 0:
                messagebox.showwarning("Atenção", "Valor final deve ser maior que zero!")
                return

            forma_pagamento = self.var_forma.get()
            parcelas = int(self.var_parcelas.get()) if forma_pagamento == "Cartão de Crédito" or forma_pagamento == "Cartão de Débito" else 1

            # Preparar itens para a venda
            itens_venda = []
            for item in self.carrinho:
                itens_venda.append({
                    "id": item[0],
                    "qtd": item[2],
                    "preco": item[3]
                })

            # Realizar venda
            sucesso, mensagem = database.realizar_venda_segura(
                self.cliente_selecionado[0],  # cliente_id
                itens_venda,
                forma_pagamento,
                parcelas,
                desconto
            )

            if sucesso:
                messagebox.showinfo("Sucesso", f"Venda finalizada!\n\n{mensagem}")
                # Fechar todas as janelas relacionadas
                self.master.destroy()  # Fecha o PDV
                self.destroy()  # Fecha o pagamento
            else:
                messagebox.showerror("Erro", f"Falha ao finalizar venda:\n{mensagem}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    # Exemplo de uso
    cliente = (1, "João Silva", "11999999999")
    carrinho = [(1, "Sapatilha A", 1, 89.90, 89.90)]
    JanelaPagamento(root, cliente, carrinho, 89.90)
    root.mainloop()