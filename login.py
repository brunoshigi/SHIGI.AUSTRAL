import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import sqlite3
import hashlib
from typing import Callable
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_LABEL, FONT_ENTRY, setup_window_icon
from utils import UIHelper


class LoginWindow:
    def __init__(self, root: tk.Tk, on_login_success: Callable):
        self.root = root
        self.root.title("AUSTRAL - LOGIN")
        self.root.geometry("400x500")
        self.config = ConfigManager()
        self.logger = AustralLogger()
        self.on_login_success = on_login_success
        
        setup_window_icon(self.root)
        self.setup_ui()
        self.init_database()
        self.center_window(400, 500)

    def setup_ui(self):
        """Configura a interface gráfica de login"""
        style = ttk.Style()
        style.configure('Custom.TEntry', padding=10)
        
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo e título
        ttk.Label(
            self.main_frame,
            text="AUSTRAL",
            font=('Helvetica', 32, 'bold'),
            bootstyle="primary"
        ).pack(pady=30)

        # Frame do formulário
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        self.create_login_form(form_frame)

    def create_login_form(self, form_frame):
        """Cria os campos e botões do formulário de login"""
        # Usuário
        ttk.Label(
            form_frame,
            text="USUÁRIO:",
            font=FONT_LABEL,
            bootstyle="primary"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            form_frame,
            width=40,
            font=FONT_ENTRY,
            style='Custom.TEntry'
        )
        self.username_entry.pack(pady=(0, 15))

        # Senha
        ttk.Label(
            form_frame,
            text="SENHA:",
            font=FONT_LABEL,
            bootstyle="primary"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            form_frame,
            width=40,
            show="•",
            font=FONT_ENTRY,
            style='Custom.TEntry'
        )
        self.password_entry.pack(pady=(0, 20))

        # Botão de login
        ttk.Button(
            form_frame,
            text="ENTRAR",
            command=self.validate_login,
            width=20,
            bootstyle="primary"
        ).pack(pady=10)

        # Label de erro
        self.error_label = ttk.Label(
            form_frame,
            text="",
            foreground="red",
            font=FONT_LABEL
        )
        self.error_label.pack(pady=10)
        
        # Bind da tecla Enter
        self.root.bind('<Return>', lambda e: self.validate_login())
        
        # Foca no campo de usuário
        self.username_entry.focus()

    def init_database(self):
        """Inicializa o banco de dados SQLite e cria o usuário admin se necessário"""
        try:
            conn = sqlite3.connect(self.config.get('database.path'))
            cursor = conn.cursor()
            
            # Cria tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')

            # Cria usuário admin se não existir
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', ('admin', admin_password, 'admin'))
            
            conn.commit()
            
        except sqlite3.Error as e:
            self.logger.logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            messagebox.showerror(
                "ERRO",
                "Erro ao inicializar banco de dados. Contate o suporte."
            )
        finally:
            conn.close()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (width / 2))
        y_coordinate = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

    @log_action("login_attempt")
    def validate_login(self):
        """Valida as credenciais de login do usuário"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.config(text="POR FAVOR, PREENCHA TODOS OS CAMPOS")
            return

        try:
            conn = sqlite3.connect(self.config.get('database.path'))
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
                self.logger.log_action(
                    "login_success",
                    username,
                    {"role": user[3]}
                )
                # Destrói o frame de login
                self.main_frame.destroy()
                # Chama a função de callback com os parâmetros necessários
                self.on_login_success(username, user[3])
            else:
                self.error_label.config(text="USUÁRIO OU SENHA INCORRETOS")
                self.logger.log_action(
                    "login_failed",
                    username,
                    {"reason": "invalid_credentials"}
                )
                
        except sqlite3.Error as e:
            self.logger.logger.error(f"Erro ao validar login: {str(e)}")
            self.error_label.config(text="ERRO AO ACESSAR BANCO DE DADOS")
        finally:
            conn.close()

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = LoginWindow(root, lambda u, r: print(f"Login success: {u} ({r})"))
    root.mainloop()