# system.py
from tkinter import messagebox
from config import ConfigManager
from logger import AustralLogger
from login import LoginWindow
from main_app import AustralApp

class AustralSystem:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.logger = AustralLogger()
        self.start_login()

    def start_login(self):
        try:
            self.login = LoginWindow(self.root, self.start_main_app)
        except Exception as e:
            self.logger.logger.error(f"Erro ao iniciar login: {str(e)}")
            messagebox.showerror("ERRO", "Erro ao iniciar tela de login")

    def start_main_app(self, username, role):
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.app = AustralApp(self.root, username, role)
        except Exception as e:
            self.logger.logger.error(f"Erro ao iniciar aplicação: {str(e)}")
            messagebox.showerror("ERRO", "Erro ao iniciar aplicação principal")