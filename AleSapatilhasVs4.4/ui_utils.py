"""
Módulo de utilitários para padronização de UI em todas as janelas do sistema.
Centraliza paleta de cores, cálculo de dimensões e estilos.
"""

import tkinter as tk

# --- PALETA DE CORES PADRONIZADA ---
PALETA = {
    "bg_fundo": "#F1F5F9",
    "bg_card": "#FFFFFF",
    "cor_borda": "#8BA2BD",
    "cor_texto": "#0B1933",
    "cor_lbl": "#020C18",
    "cor_destaque": "#6366F1",
    "cor_btn_menu": "#1E293B",
    "cor_btn_sair": "#25324E",
    "cor_btn_acao": "#425074",
    "cor_hover_btn": "#6F7CA0",
    "cor_hover_field": "#484AD6"
}

def calcular_dimensoes_janela(root, largura_desejada=600, altura_desejada=800, maximizar=False):
    """
    Calcula e define as dimensões da janela respeitando:
    - Tamanho do monitor
    - Barra de tarefas do SO
    - Centralização na tela
    
    Args:
        root: Janela Tkinter
        largura_desejada: Largura desejada (padrão 600)
        altura_desejada: Altura desejada (padrão 800)
        maximizar: Se True, maximiza; se False, usa dimensões padrão
    """
    # Atualiza para capturar dimensões corretas
    root.update_idletasks()
    
    # Dimensões do monitor (aproximadamente)
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    
    if maximizar:
        # Maximiza deixando espaço para barra de tarefas (~70px)
        root.geometry(f"{largura_tela}x{altura_tela - 70}+0+0")
    else:
        # Usa dimensões padrão
        # Verifica se o tamanho desejado cabe na tela
        largura_final = min(largura_desejada, largura_tela - 20)
        altura_final = min(altura_desejada, altura_tela - 100)
        
        # Centraliza a janela
        x = (largura_tela - largura_final) // 2
        y = (altura_tela - altura_final) // 2
        
        root.geometry(f"{largura_final}x{altura_final}+{x}+{y}")

def get_paleta():
    """Retorna a paleta de cores padronizada"""
    return PALETA.copy()

def criar_style_padrao(root):
    """Configura estilos padrão para ttk.Combobox e ttk.Treeview"""
    from tkinter import ttk
    
    style = ttk.Style()
    style.theme_use('clam')
    
    # Combobox
    style.configure("TCombobox", 
                   fieldbackground=PALETA["bg_card"],
                   background=PALETA["bg_card"],
                   arrowcolor=PALETA["cor_btn_acao"],
                   bordercolor=PALETA["cor_borda"])
    
    # Treeview
    style.configure("Treeview",
                   background=PALETA["bg_card"],
                   foreground=PALETA["cor_texto"],
                   rowheight=22,
                   borderwidth=0,
                   font=("Segoe UI", 9))
    
    style.configure("Treeview.Heading",
                   font=("Segoe UI", 10, "bold"),
                   background=PALETA["bg_card"])
    
    style.map("Treeview",
             background=[('selected', PALETA["cor_destaque"])])
    
    return style
