import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
# Certifique-se de que o arquivo 'database.py' tenha as funções chamadas no método 'atualizar'

class JanelaCadastroPedidos(tk.Toplevel):
    def __init__(self, master, dados_venda):
        super().__init__(master)
               
        # --- PALETA DE CORES ---
        self.bg_fundo = "#f4f5f9"
        self.bg_card = "#ffffff"
        self.cor_borda = "#d1d5db"
        self.cor_texto = "#1f2937"
        self.cor_lbl = "#4b5563"
        self.cor_btn_1 = "#4b5563"   
        self.cor_btn_2 = "#374151"   
        self.cor_btn_sair = "#1f2937" 
        self.cor_hover_field = "#3b82f6"   
        self.cor_hover_btn = "#6b7280"

        self.title("Alê Sapatilhas - Painel de Pedidos")
        self.geometry("450x750")
        self.configure(bg=self.bg_fundo)
        
        # Proteção contra dados incompletos
        if not dados_venda or len(dados_venda) < 5:
            messagebox.showerror("Erro", "Dados da venda insuficientes.")
            self.destroy()
            return

        self.venda_id = dados_venda[0]
        self.criar_widgets(dados_venda)
        self.grab_set()

    def criar_treeview(self, parent, colunas, cabecalhos, altura):
        frame_tree = tk.Frame(parent, bg=self.bg_card, highlightbackground=self.cor_borda, highlightthickness=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=self.bg_card, 
                        foreground=self.cor_texto, 
                        fieldbackground=self.bg_card, 
                        rowheight=25, 
                        font=("Segoe UI", 9))
        
        style.configure("Treeview.Heading", 
                        background=self.bg_fundo, 
                        foreground=self.cor_lbl, 
                        font=("Segoe UI", 9, "bold"), 
                        relief="flat")
        
        style.map("Treeview", background=[('selected', self.cor_hover_field)])

        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", height=altura)
        for col, head in zip(colunas, cabecalhos):
            tree.heading(col, text=head)
            # Ajuste dinâmico de largura para a coluna principal
            largura = 200 if "Nome" in head or "Produto" in head else 80
            tree.column(col, anchor="center", width=largura)

        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return frame_tree, tree

    def criar_widgets(self, d):
        main_frame = tk.Frame(self, bg=self.bg_fundo, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text=f"PEDIDO: #{self.venda_id}", bg=self.bg_fundo, 
                 fg=self.cor_texto, font=("Segoe UI", 14, "bold")).pack(anchor="w")

        # --- SEÇÃO: CLIENTE ---
        tk.Label(main_frame, text="DADOS DO CLIENTE", bg=self.bg_fundo, 
                 fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(15, 5))
        
        f_cli, self.tree_cli = self.criar_treeview(main_frame, ("id", "nome", "tel"), 
                                                   ("ID", "Nome do Cliente", "Telefone"), 2)
        f_cli.pack(fill="x")
        # Idealmente, buscar telefone do banco via ID do cliente
        self.tree_cli.insert("", "end", values=("?", d[1], "Ver cadastro..."))

        # --- SEÇÃO: PRODUTOS ---
        tk.Label(main_frame, text="PRODUTOS DO PEDIDO", bg=self.bg_fundo, 
                 fg=self.cor_lbl, font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(15, 5))
        
        f_prod, self.tree_prod = self.criar_treeview(main_frame, ("prod", "qtd", "subtotal"), 
                                                     ("Produto", "Qtd", "Subtotal"), 6)
        f_prod.pack(fill="both", expand=True)
        # Mock melhorado com o valor real da venda
        self.tree_prod.insert("", "end", values=("Resumo da Venda", "-", f"R$ {d[2]:.2f}"))

        # --- STATUS ---
        status_frame = tk.Frame(main_frame, bg=self.bg_fundo)
        status_frame.pack(fill="x", pady=20)

        # Trata possíveis valores nulos ou diferentes vindo do banco
        self.var_venda = tk.StringVar(value=d[3] if d[3] else "Pendente")
        self.var_entrega = tk.StringVar(value=d[4] if d[4] else "À Entregar")

        for label, var, opts in [("PAGAMENTO", self.var_venda, ["Pendente", "Confirmada", "Cancelada"]),
                                 ("LOGÍSTICA", self.var_entrega, ["À Entregar", "Em Trânsito", "Entregue"])]:
            container = tk.Frame(status_frame, bg=self.bg_fundo)
            container.pack(side="left", fill="x", expand=True, padx=5)
            tk.Label(container, text=label, bg=self.bg_fundo, fg=self.cor_lbl, font=("Segoe UI", 7, "bold")).pack(anchor="w")
            
            # Usando OptionMenu com estilo manual
            opt = tk.OptionMenu(container, var, *opts)
            opt.config(bg=self.bg_card, relief="flat", highlightthickness=1, highlightbackground=self.cor_borda, font=("Segoe UI", 9))
            opt["menu"].config(bg=self.bg_card, font=("Segoe UI", 9))
            opt.pack(fill="x", pady=2)

        # --- BOTÕES ---
        btn_container = tk.Frame(main_frame, bg=self.bg_fundo)
        btn_container.pack(fill="x", side="bottom", pady=5)

        linha1 = tk.Frame(btn_container, bg=self.bg_fundo)
        linha1.pack(fill="x", pady=2)
        
        self.criar_botao(linha1, "VER CLIENTE", self.cor_btn_1, self.abrir_clientes).pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.criar_botao(linha1, "VER VENDAS", self.cor_btn_1, self.abrir_vendas).pack(side="left", fill="x", expand=True, padx=(2, 0))

        self.criar_botao(btn_container, "ATUALIZAR", self.cor_btn_2, self.atualizar).pack(fill="x", pady=2, ipady=5)
        self.criar_botao(btn_container, "FECHAR", self.cor_btn_sair, self.destroy).pack(fill="x", pady=2)

    def criar_botao(self, parent, texto, cor, comando):
        btn = tk.Button(parent, text=texto, bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                        relief="flat", cursor="hand2", command=comando)
        btn.bind("<Enter>", lambda e: btn.config(bg=self.cor_hover_btn))
        btn.bind("<Leave>", lambda e: btn.config(bg=cor))
        return btn

    def atualizar(self):
        try:
            import database
            database.atualizar_status_venda_financeiro(self.venda_id, self.var_venda.get())
            database.atualizar_status_entrega(self.venda_id, self.var_entrega.get())
            messagebox.showinfo("Sucesso", f"Pedido #{self.venda_id} atualizado!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar banco: {e}")

    # Métodos de abertura de janelas (abrir_clientes, abrir_vendas) permanecem iguais

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    JanelaCadastroPedidos(root)
    root.mainloop()