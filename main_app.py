import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Window
from datetime import datetime
from typing import Callable, List, Dict
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_TITLE, FONT_LABEL, setup_window_icon
from PIL import Image, ImageTk  # Importar para manipulação de imagens

# Importação dos módulos
from mix import MixDiarioApp
from delivery import EtiquetaClientesApp
from transfer import EtiquetaTransferenciaApp
from mail import EmailGeneratorApp
from defects import DefectManagerApp
from sinoms import PedidoSinOMSApp 

class AustralApp:
    def __init__(self, root: tk.Tk, username: str, role: str):
        self.root = root
        self.username = username
        self.role = role
        self.config = ConfigManager()
        self.logger = AustralLogger()
        
        self.root.title("SISTEMA AUSTRAL - INTERFACE DO FUNCIONÁRIO")
        self.root.geometry("800x600")
        self.center_window()
        setup_window_icon(self.root)
        
        self.setup_ui()
        self.logger.log_action("app_start", self.username, {"role": self.role})

    def center_window(self):
        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def setup_ui(self):
        """Configura a interface principal do sistema Austral"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho
        self.create_header()
        
        # Container de botões
        self.buttons_container = ttk.Frame(self.main_frame)
        self.buttons_container.pack(fill=tk.BOTH, expand=True, pady=18)
        self.create_function_buttons()
        
        # Rodapé
        self.create_footer()

    def create_header(self):
        """Cria o cabeçalho com título e informações do usuário"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        # Logo e título
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Carrega a imagem do logotipo
        try:
            logo_image = Image.open("logo.png")  # Substitua pelo caminho correto do seu logotipo
            logo_image = logo_image.resize((50, 50), Image.ANTIALIAS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(title_frame, image=logo_photo)
            logo_label.image = logo_photo  # Mantém a referência
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            self.logger.logger.error(f"Erro ao carregar logotipo: {str(e)}")

        title_label = ttk.Label(
            title_frame,
            text="SISTEMA AUSTRAL",
            font=FONT_TITLE,
        )
        title_label.pack(side=tk.LEFT)

        # Informações do usuário
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        
        user_info = ttk.Label(
            user_frame,
            text=f"Bem-vindo, {self.username}",
            font=FONT_LABEL
        )
        user_info.pack()

    def create_function_buttons(self):
        """Cria os botões de funcionalidades"""
        functions: List[Dict] = [
            {
            'title': 'REGISTRO VM DIÁRIO',
            'command': self.open_mix_diario,
            },
            {
            'title': 'CONTROLE PEDIDOS SINOMS',
            'command': self.open_sinoms_control,
            },
            {
            'title': 'PLANILHA DE DEFEITOS',
            'command': self.open_defect_manager,
            },
            {
            'title': 'E-MAIL DE FECHAMENTO',
            'command': self.open_email_generator,
            },
            {
            'title': 'ETIQUETA ENTREGA CLIENTES',
            'command': self.open_etiquetas_clientes,
            },
            {
            'title': 'ETIQUETA TRANSFERÊNCIA FILIAIS',
            'command': self.open_etiquetas_transferencia,
            }
        ]

        # Cria botões com estilo personalizado
        style = ttk.Style()
        style.configure('Function.TButton',
                        font=('Helvetica', 10, 'bold'),
                        width=33) 

        for func in functions:
            button = ttk.Button(
                self.buttons_container,
                text=func['title'],
                command=func['command'],
                style='Function.TButton',
                bootstyle="primary"
            )
            button.pack(pady=10)

    @log_action("open_email_generator")
    def open_email_generator(self):
        """Abre a janela do Gerador de E-mail"""
        window = ttk.Toplevel(self.root)
        window.title("GERADOR DE E-MAIL - FECHAMENTO")
        EmailGeneratorApp(window)

    @log_action("open_mix_diario")
    def open_mix_diario(self):
        """Abre a janela do Mix Diário"""
        window = ttk.Toplevel(self.root)
        window.title("MIX DIÁRIO")
        MixDiarioApp(window)

    @log_action("open_etiquetas_clientes")
    def open_etiquetas_clientes(self):
        """Abre a janela para gerar etiqueta para clientes"""
        window = ttk.Toplevel(self.root)
        window.title("ETIQUETA DE CLIENTES")
        EtiquetaClientesApp(window)

    @log_action("open_etiquetas_transferencia")
    def open_etiquetas_transferencia(self):
        """Abre a janela para gerar etiqueta de transferência"""
        window = ttk.Toplevel(self.root)
        window.title("ETIQUETA DE TRANSFERÊNCIA")
        EtiquetaTransferenciaApp(window)

    @log_action("open_defect_manager")
    def open_defect_manager(self):
        """Abre a janela do Gerenciador de Peças com Defeito"""
        window = ttk.Toplevel(self.root)
        window.title("GERENCIADOR DE PEÇAS COM DEFEITO")
        DefectManagerApp(window)

    @log_action("open_sinoms_control")
    def open_sinoms_control(self):
        """Abre a janela do Controle de Pedidos SinOMS"""
        window = ttk.Toplevel(self.root)
        window.title("CONTROLE DE PEDIDOS SINOMS")
        PedidoSinOMSApp(window)

    def create_footer(self):
        """Cria o rodapé com informações e botão de logout"""
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, pady=(3, 0))

        # Status
        status_label = ttk.Label(
            footer_frame,
            text=(
                f"Conectado como {self.username} | "
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
            ),
            font=('Helvetica', 10)
        )
        status_label.pack(side=tk.LEFT)

        # Botão de logout
        logout_button = ttk.Button(
            footer_frame,
            text="SAIR",
            command=self.logout,
            bootstyle="danger"
        )
        logout_button.pack(side=tk.RIGHT)

        # Marca d'água no canto inferior direito
        watermark = ttk.Label(
            self.main_frame,
            text="@brunoshigi github",
            font=('Helvetica', 7),
            foreground='#475569'
        )
        watermark.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=5)

    @log_action("logout")
    def logout(self):
        """Realiza o logout do usuário"""
        if messagebox.askyesno("LOGOUT", "Deseja realmente sair do sistema?"):
            self.logger.log_action("logout_success", self.username)
            self.root.destroy()


if __name__ == "__main__":
    root = Window(themename="litera")
    app = AustralApp(root, "admin", "admin")
    root.mainloop()
