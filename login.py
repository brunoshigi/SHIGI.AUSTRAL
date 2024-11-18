# login.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sqlite3
import hashlib
from typing import Callable
import requests
import threading
import time
from datetime import datetime
from PIL import Image, ImageTk
import webbrowser

# Importações dos seus módulos
from utils import (
    FONT_LABEL, FONT_ENTRY, FONT_BUTTON,
    ResourceManager, ThemeManager, UIHelper,
    setup_window_icon, theme_manager, resource_manager, ui_helper
)
from config import ConfigManager
from logger import AustralLogger

class LoginWindow:
    def __init__(self, root: tk.Tk, on_login_success: Callable):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("AUSTRAL - LOGIN")
        self.config = ConfigManager()
        self.logger = AustralLogger()
        self.resource_manager = resource_manager  # Usando a instância global
        self.ui_helper = ui_helper  # Usando a instância global
        self.theme_manager = theme_manager  # Usando a instância global

        # Configura o ícone da janela usando o ResourceManager
        setup_window_icon(self.root)

        # Configura a interface gráfica
        self.setup_ui()

        # Centraliza a janela usando o UIHelper
        self.ui_helper.center_window(self.root, 400, 540)

        # Inicia a thread de atualização das cotações
        self.update_thread = threading.Thread(target=self.update_currency_loop, daemon=True)
        self.update_thread.start()

    def setup_ui(self):
        """Configura a interface gráfica de login"""
        style = ttk.Style()
        style.theme_use('litera')  # Usa o tema 'litera'
        style.configure('Custom.TEntry', padding=8)

        # Cores personalizadas
        COLORS = {
            'background': '#FFFFFF',  # Branco
            'card_bg': '#F8F9FA',  # Cinza claro
            'text_dark': '#1E293B',  # Azul escuro
            'text_medium': '#475569',  # Cinza escuro
            'value_color': '#334155',  # Azul escuro
            'accent': '#334155',  # Azul escuro
            'border': '#E2E8F0',  # Cinza claro
            'button': '#007BFF',  # Botão azul padrão
            'error': '#DC2626'  # Vermelho
        }

        # Configurações de estilo para os displays de cotação
        style.configure('Currency.TLabel',
                        font=('Helvetica', 10, 'bold'),
                        padding=5,
                        background=COLORS['card_bg'],
                        foreground=COLORS['value_color'])

        style.configure('CurrencySymbol.TLabel',
                        font=('Helvetica', 10, 'bold'),
                        foreground=COLORS['accent'])

        style.configure('Currency.TFrame',
                        background=COLORS['card_bg'],
                        relief="solid",
                        borderwidth=1)

        style.configure('Title.TLabel',
                        font=('Helvetica', 24, 'bold'),
                        foreground=COLORS['accent'])

        style.configure('Header.TLabel',
                        font=('Helvetica', 8, 'bold'),
                        foreground=COLORS['text_medium'])

        # Estilo para botões personalizados
        style.configure('Custom.TButton',
                        font=FONT_BUTTON,
                        foreground='white',
                        background=COLORS['button'],
                        borderwidth=0)

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo e título
        # Carrega a imagem do logotipo usando o ResourceManager
        try:
            logo_path = self.resource_manager.get_resource_path('logo.png')  # Caminho na raiz
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((100, 100), Image.ANTIALIAS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(self.main_frame, image=logo_photo)
            logo_label.image = logo_photo  # Mantém a referência
            logo_label.pack(pady=5)
        except Exception as e:
            print(f"Erro ao carregar logotipo: {str(e)}")
            # Se não puder carregar a imagem, apenas mostra o título
            ttk.Label(
                self.main_frame,
                text="AUSTRAL",
                style='Title.TLabel'
            ).pack(pady=10)

        # Frame do formulário
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        self.create_login_form(form_frame)

        # Frame para as cotações com título
        quotes_title_frame = ttk.Frame(self.main_frame)
        quotes_title_frame.pack(fill=tk.X, padx=8, pady=(5, 3))

        ttk.Label(
            quotes_title_frame,
            text="COTAÇÕES DO DIA",
            style='Header.TLabel'
        ).pack(side=tk.LEFT)

        # Container para os cards de cotação
        currency_container = ttk.Frame(self.main_frame)
        currency_container.pack(fill=tk.X, padx=15)

        # Frame para USD
        usd_frame = ttk.Frame(currency_container)
        usd_frame.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        ttk.Label(
            usd_frame,
            text="$",
            style='CurrencySymbol.TLabel'
        ).pack(pady=(0, 2))

        # Frame para o valor do USD com borda
        usd_value_frame = ttk.Frame(usd_frame, style='Currency.TFrame')
        usd_value_frame.pack(fill=tk.X)

        self.usd_label = ttk.Label(
            usd_value_frame,
            text="CARREGANDO...",
            style='Currency.TLabel',
            width=12
        )
        self.usd_label.pack(padx=9, pady=4)

        # Frame para EUR
        eur_frame = ttk.Frame(currency_container)
        eur_frame.pack(side=tk.LEFT, expand=True, padx=(5, 0))

        ttk.Label(
            eur_frame,
            text="€",
            style='CurrencySymbol.TLabel'
        ).pack(pady=(0, 2))

        # Frame para o valor do EUR com borda
        eur_value_frame = ttk.Frame(eur_frame, style='Currency.TFrame')
        eur_value_frame.pack(fill=tk.X)

        self.eur_label = ttk.Label(
            eur_value_frame,
            text="CARREGANDO...",
            style='Currency.TLabel',
            width=10
        )
        self.eur_label.pack(padx=8, pady=5)

        # Label para última atualização
        self.update_label = ttk.Label(
            self.main_frame,
            text="ATUALIZAÇÃO AUTOMÁTICA A CADA 10 MINUTOS",
            font=('Helvetica', 8),
            foreground=COLORS['text_medium']
        )
        self.update_label.pack(pady=(4, 0))

        # Marca d'água no canto inferior direito
        watermark = ttk.Label(
            self.main_frame,
            text="@brunoshigi github",
            font=('Helvetica', 7),
            foreground=COLORS['text_medium']
        )
        watermark.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=5)

    def add_placeholder(self, entry, placeholder_text):
        entry.insert(0, placeholder_text)
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, placeholder_text))
        entry.bind("<FocusOut>", lambda event: self.add_placeholder_text(event, placeholder_text))

    def clear_placeholder(self, event, placeholder_text):
        if event.widget.get() == placeholder_text:
            event.widget.delete(0, tk.END)

    def add_placeholder_text(self, event, placeholder_text):
        if not event.widget.get():
            event.widget.insert(0, placeholder_text)

    def toggle_password_visibility(self):
        if self.password_entry.cget('show') == '•':
            self.password_entry.config(show='')
            self.show_password_button.config(text='OCULTAR')
        else:
            self.password_entry.config(show='•')
            self.show_password_button.config(text='MOSTRAR')

    def create_login_form(self, form_frame):
        """Cria os campos e botões do formulário de login"""
        COLORS = {
            'text_dark': '#1E293B',
            'text_medium': '#475569',
            'button': '#007BFF',
            'error': '#DC2626'
        }

        # Usuário
        ttk.Label(
            form_frame,
            text="USUÁRIO:",
            font=FONT_LABEL,
            foreground=COLORS['text_medium']
        ).pack(anchor=tk.W, pady=(0, 4))

        self.username_entry = ttk.Entry(
            form_frame,
            width=38,
            font=FONT_ENTRY,
            style='Custom.TEntry'
        )
        self.username_entry.pack(pady=(0, 8))

        # Adiciona placeholder
        self.add_placeholder(self.username_entry, "DIGITE SEU USUÁRIO")  # Texto em maiúsculas

        # Senha
        ttk.Label(
            form_frame,
            text="SENHA:",
            font=FONT_LABEL,
            foreground=COLORS['text_medium']
        ).pack(anchor=tk.W, pady=(0, 4))

        self.password_entry = ttk.Entry(
            form_frame,
            width=38,
            show="•",
            font=FONT_ENTRY,
            style='Custom.TEntry'
        )
        self.password_entry.pack(pady=(0, 2))

        # Adiciona placeholder
        self.add_placeholder(self.password_entry, "DIGITE SUA SENHA")  # Texto em maiúsculas

        # Botão para mostrar/ocultar senha
        self.show_password_button = ttk.Button(
            form_frame,
            text="MOSTRAR",
            command=self.toggle_password_visibility,
            style='Custom.TButton'
        )
        self.show_password_button.pack(pady=(4, 8))

        # "Lembrar-me" checkbox
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(
            form_frame,
            text="LEMBRAR-ME",  # Texto em maiúsculas
            variable=self.remember_var
        )
        remember_check.pack(pady=3)

        # "Esqueceu a senha?" link
        forgot_password_link = ttk.Label(
            form_frame,
            text="ESQUECEU A SENHA?",  # Texto em maiúsculas
            foreground="red",
            cursor="hand2"
        )
        forgot_password_link.pack()
        forgot_password_link.bind("<Button-1>", lambda e: self.redirect_to_whatsapp())

        # Botão de login com estilo personalizado
        login_button = ttk.Button(
            form_frame,
            text="ENTRAR",
            command=self.validate_login,
            width=28,
            style='Custom.TButton'
        )
        login_button.pack(pady=8)

        # Label de erro
        self.error_label = ttk.Label(
            form_frame,
            text="",
            foreground=COLORS['error'],
            font=FONT_LABEL
        )
        self.error_label.pack(pady=5)

        # Bind da tecla Enter
        self.root.bind('<Return>', lambda e: self.validate_login())

        # Foca no campo de usuário
        self.username_entry.focus()

    def update_currency_rates(self):
        """Atualiza as cotações do dólar e euro"""
        try:
            response = requests.get('https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL')
            data = response.json()

            # Atualiza os labels com as novas cotações
            usd_rate = float(data['USDBRL']['bid'])
            eur_rate = float(data['EURBRL']['bid'])

            self.usd_label.config(text=f"R$ {usd_rate:.2f}")
            self.eur_label.config(text=f"R$ {eur_rate:.2f}")

            # Atualiza o horário
            current_time = datetime.now().strftime('%H:%M:%S')
            self.update_label.config(text=f"ÚLTIMA ATUALIZAÇÃO: {current_time}")  # Texto em maiúsculas

        except Exception as e:
            print(f"Erro ao atualizar cotações: {str(e)}")
            self.usd_label.config(text="ERRO")
            self.eur_label.config(text="ERRO")

    def update_currency_loop(self):
        """Loop para atualizar as cotações periodicamente"""
        while True:
            self.update_currency_rates()
            time.sleep(600)  # Atualiza a cada 10 minutos

    def validate_login(self):
        """Valida as credenciais de login do usuário"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Remove placeholders se presentes
        if username == "DIGITE SEU USUÁRIO":
            username = ""
        if password == "DIGITE SUA SENHA":
            password = ""

        if not username or not password:
            self.error_label.config(text="POR FAVOR, PREENCHA TODOS OS CAMPOS")
            return

        try:
            # Obter o caminho do banco de dados
            db_path = self.config.get('database.path')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Verifica credenciais
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))

            user = cursor.fetchone()

            if user:
                # Atualiza último login
                cursor.execute('''
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE username = ?
                ''', (username,))
                conn.commit()

                self.error_label.config(text="")
                self.logger.log_action("login_success", username, {"role": user[3]})

                # Chama a função de callback com os parâmetros necessários
                self.on_login_success(username, user[3])
            else:
                self.error_label.config(text="USUÁRIO OU SENHA INCORRETOS")
                self.logger.log_action("login_failed", username, {"reason": "invalid_credentials"})

        except sqlite3.Error as e:
            print(f"Erro ao validar login: {str(e)}")
            self.error_label.config(text="ERRO AO ACESSAR BANCO DE DADOS")
        finally:
            conn.close()

    def redirect_to_whatsapp(self):
        """Redireciona para o WhatsApp para recuperação de senha"""
        webbrowser.open("https://wa.me/5511983988868")
