import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

class AustralMenu:
    def __init__(self, root):
        # Configuração da janela principal
        self.root = root
        self.root.title("SISTEMA AUSTRAL v1.0")
        self.root.geometry("1000x550")
        self.root.configure(bg='#0a0a1f')
        
        # Criando fontes personalizadas
        self.title_font = ('Helvetica', 24, 'bold')
        self.button_font = ('Helvetica', 11, 'bold')
        self.section_font = ('Helvetica', 14, 'bold')
        
        # Carregando ícone genérico
        # Substitua este caminho pelo caminho do seu ícone ou crie diferentes variáveis para cada botão
        try:
            self.icon_generic = tk.PhotoImage(file='icons/generic_icon.png')
        except:
            # Caso não encontre a imagem, desenha um ícone "emojis" (por exemplo) ou simplesmente ignore
            self.icon_generic = None
        
        # Frame principal
        main_frame = tk.Frame(root, bg='#0a0a1f', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        # Título principal (com efeito neon)
        title_frame = tk.Frame(main_frame, bg='#0a0a1f')
        title_frame.pack(fill='x', pady=(0, 30))
        
        title = tk.Label(title_frame,
                         text="SISTEMA AUSTRAL",
                         font=self.title_font,
                         fg='#00ff9f',
                         bg='#0a0a1f',
                         pady=15)
        title.pack()
        
        subtitle = tk.Label(title_frame,
                            text="// INTERFACE DO FUNCIONÁRIO //",
                            font=('Helvetica', 10),
                            fg='#0099ff',
                            bg='#0a0a1f')
        subtitle.pack()
        
        # Container para as seções (grid para melhor alinhamento)
        sections_container = tk.Frame(main_frame, bg='#0a0a1f')
        sections_container.pack(expand=True, fill='both')
        
        # Configuração das colunas no container para expandir igualmente
        sections_container.grid_columnconfigure(0, weight=1)
        sections_container.grid_columnconfigure(1, weight=1)
        sections_container.grid_columnconfigure(2, weight=1)
        
        # Criando as seções
        self.criar_secao(sections_container, "OPERAÇÕES DIÁRIAS", [
            "REGISTRO VM DIÁRIO",
            "E-MAIL DE FECHAMENTO",
            "SIMULADOR DE VENDAS"
        ], 0, '#ff0055')
        
        self.criar_secao(sections_container, "GESTÃO DE PRODUTOS", [
            "PLANILHA DE DEFEITOS",
            "INVENTÁRIO",
            "CONTROLE PEDIDOS SINOMS"
        ], 1, '#00ffff')
        
        self.criar_secao(sections_container, "IMPRESSÃO DE ETIQUETAS", [
            "ENTREGA CLIENTES",
            "TRANSFERÊNCIA FILIAIS"
        ], 2, '#ff9900')
        
        # Rodapé
        footer_frame = tk.Frame(main_frame, bg='#0a0a1f')
        footer_frame.pack(fill='x', pady=(20, 0))
        
        tk.Label(footer_frame,
                 text="SISTEMA AUSTRAL v1.0 | GitHub @brunoshigi",
                 font=('Helvetica', 8),
                 fg='#666699',
                 bg='#0a0a1f').pack(side='right')

    def criar_secao(self, container, titulo, ferramentas, coluna, cor_neon):
        """Cria uma seção de ferramentas com título e botões, em colunas do grid"""
        secao = tk.Frame(container, bg='#0a0a1f')
        secao.grid(row=0, column=coluna, padx=20, sticky='nsew')
        
        # Título da seção
        tk.Label(secao,
                 text=titulo,
                 font=self.section_font,
                 fg=cor_neon,
                 bg='#0a0a1f',
                 pady=10).pack(fill='x')
        
        # Frame para os botões
        botoes_frame = tk.Frame(secao, bg='#0a0a1f', pady=10)
        botoes_frame.pack(fill='x')
        
        # Criando os botões da seção
        for ferramenta in ferramentas:
            btn = tk.Button(
                botoes_frame,
                text=ferramenta,
                font=self.button_font,
                fg='white',
                bg='#1a1a3c',
                activebackground='#2a2a4c',
                activeforeground=cor_neon,
                relief='flat',
                pady=8,
                borderwidth=0,
                width=25,
                cursor='hand2',
                command=lambda f=ferramenta: self.abrir_ferramenta(f),
                # Aqui usamos o ícone genérico e colocamos o texto à direita (compound='left')
                image=self.icon_generic,
                compound='left'
            )
            
            btn.pack(pady=5, fill='x')
            
            # Adiciona eventos para efeito hover
            btn.bind('<Enter>', lambda e, b=btn, c=cor_neon: self.on_hover(b, c))
            btn.bind('<Leave>', lambda e, b=btn: self.on_leave(b))

    def on_hover(self, button, cor_neon):
        """Efeito ao passar o mouse sobre o botão"""
        button.configure(bg='#2a2a4c', fg=cor_neon)

    def on_leave(self, button):
        """Efeito ao remover o mouse do botão"""
        button.configure(bg='#1a1a3c', fg='white')

    def abrir_ferramenta(self, nome_ferramenta):
        """Função para abrir a ferramenta selecionada"""
        print(f"Iniciando {nome_ferramenta}...")

if __name__ == "__main__":
    root = tk.Tk()
    app = AustralMenu(root)
    root.mainloop()
