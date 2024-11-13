"""
Módulo de utilitários para o sistema Austral.
Contém definições de temas, recursos e funções utilitárias comuns.
"""

from pathlib import Path
from typing import Dict, Optional, Any, Union, Tuple
import tkinter as tk
from tkinter import messagebox
import sys
import os
import json
import shutil
from datetime import datetime


# Constantes de fonte globais
FONT_TITLE = ("Helvetica", 16, "bold")
FONT_LABEL = ("Helvetica", 12)
FONT_SUBTITLE = ("Helvetica", 14)
FONT_ENTRY = ("Helvetica", 12)
FONT_BUTTON = ("Helvetica", 12, "bold")

class ThemeManager:
    """Gerenciador de temas e estilos da aplicação"""
    
    FONTS = {
        'title': FONT_TITLE,
        'subtitle': FONT_SUBTITLE,
        'label': FONT_LABEL,
        'entry': FONT_ENTRY,
        'button': FONT_BUTTON
    }

    COLORS = {
        'primary': '#0d47a1',
        'secondary': '#0f9d58',
        'background': '#ffffff',
        'text': '#202124',
        'error': '#d93025',
        'success': '#0f9d58',
        'warning': '#f4b400',
        'info': '#4285f4'
    }

    STYLES = {
        'default': {
            'font': FONTS['label'],
            'background': COLORS['background'],
            'foreground': COLORS['text']
        },
        'header': {
            'font': FONTS['title'],
            'background': COLORS['primary'],
            'foreground': COLORS['background']
        },
        'error_message': {
            'font': FONTS['label'],
            'foreground': COLORS['error']
        }
    }

    @classmethod
    def get_font(cls, font_type: str) -> tuple:
        """Retorna a fonte especificada ou a fonte padrão se não encontrada"""
        return cls.FONTS.get(font_type, cls.FONTS['label'])

    @classmethod
    def get_color(cls, color_type: str) -> str:
        """Retorna a cor especificada ou a cor primária se não encontrada"""
        return cls.COLORS.get(color_type, cls.COLORS['primary'])

    @classmethod
    def get_style(cls, style_type: str) -> dict:
        """Retorna o estilo especificado ou o estilo padrão se não encontrado"""
        return cls.STYLES.get(style_type, cls.STYLES['default'])

    @classmethod
    def apply_theme(cls, widget: tk.Widget, style_type: str = 'default') -> None:
        """Aplica um estilo específico a um widget"""
        style = cls.get_style(style_type)
        widget.configure(**style)


class ResourceManager:
    """Gerenciador de recursos da aplicação"""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.resource_dirs = {
            'assets': self.base_dir / 'assets',
            'temp': self.base_dir / 'temp',
            'logs': self.base_dir / 'logs',
            'data': self.base_dir / 'data'
        }
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Garante que todos os diretórios de recursos existam"""
        for dir_path in self.resource_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_resource_path(self, resource_type: str, filename: str) -> Path:
        """
        Retorna o caminho completo para um recurso
        
        Args:
            resource_type: Tipo do recurso ('assets', 'temp', 'logs', 'data')
            filename: Nome do arquivo
        
        Returns:
            Path: Caminho completo para o recurso
        
        Raises:
            ValueError: Se o tipo de recurso for inválido
        """
        if resource_type not in self.resource_dirs:
            raise ValueError(f"Tipo de recurso inválido: {resource_type}")
        
        return self.resource_dirs[resource_type] / filename

    def setup_window_icon(self, window: tk.Tk) -> None:
        """Configura o ícone da janela"""
        try:
            icon_path = self.get_resource_path('assets', 'icone.ico')
            if icon_path.exists():
                if os.name == 'nt':  # Windows
                    window.iconbitmap(default=str(icon_path))
                else:  # Linux/Mac
                    icon = tk.PhotoImage(file=str(icon_path))
                    window.iconphoto(True, icon)
        except Exception as e:
            print(f"Erro ao configurar ícone: {e}")

    def save_temp_file(self, content: Union[str, bytes], filename: str, mode: str = 'w') -> Path:
        """
        Salva um arquivo temporário
        
        Args:
            content: Conteúdo a ser salvo
            filename: Nome do arquivo
            mode: Modo de escrita ('w' para texto, 'wb' para binário)
        
        Returns:
            Path: Caminho do arquivo salvo
        """
        temp_path = self.get_resource_path('temp', filename)
        with open(temp_path, mode) as f:
            f.write(content)
        return temp_path

    def cleanup_temp_files(self, max_age_days: int = 7) -> None:
        """
        Limpa arquivos temporários mais antigos que max_age_days
        
        Args:
            max_age_days: Idade máxima dos arquivos em dias
        """
        temp_dir = self.resource_dirs['temp']
        cutoff = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        for file_path in temp_dir.glob('*'):
            if file_path.stat().st_mtime < cutoff:
                file_path.unlink()


class UIHelper:
    """Classe auxiliar para operações comuns de interface"""

    @staticmethod
    def center_window(window: tk.Tk, width: int, height: int) -> None:
        """
        Centraliza uma janela na tela
        
        Args:
            window: Janela a ser centralizada
            width: Largura desejada
            height: Altura desejada
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def show_message(
        title: str,
        message: str,
        message_type: str = "info"
    ) -> None:
        """
        Mostra uma mensagem padronizada
        
        Args:
            title: Título da mensagem
            message: Conteúdo da mensagem
            message_type: Tipo da mensagem ('info', 'warning', 'error', 'question')
        """
        message_functions = {
            'info': messagebox.showinfo,
            'warning': messagebox.showwarning,
            'error': messagebox.showerror,
            'question': messagebox.askquestion
        }
        
        func = message_functions.get(message_type, messagebox.showinfo)
        return func(title, message)

    @staticmethod
    def validate_entry(
        value: str,
        validation_type: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Valida o conteúdo de um Entry
        
        Args:
            value: Valor a ser validado
            validation_type: Tipo de validação ('text', 'number', 'email', etc)
            min_length: Comprimento mínimo permitido
            max_length: Comprimento máximo permitido
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if min_length and len(value) < min_length:
            return False
        
        if max_length and len(value) > max_length:
            return False
            
        validations = {
            'text': str.isalpha,
            'number': str.isdigit,
            'email': lambda x: '@' in x and '.' in x.split('@')[1],
            'alphanumeric': str.isalnum
        }
        
        validator = validations.get(validation_type, lambda x: True)
        return validator(value)


# Constantes globais úteis
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DEFAULT_ENCODING = "utf-8"

# Funções utilitárias globais
def format_currency(value: float) -> str:
    """Formata um valor para moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_date(date_str: str) -> datetime:
    """Converte uma string de data para objeto datetime"""
    return datetime.strptime(date_str, DATE_FORMAT)

def format_date(date: datetime) -> str:
    """Formata um objeto datetime para string de data"""
    return date.strftime(DATE_FORMAT)

# Função auxiliar para configuração de janela
def setup_window_icon(window: tk.Tk) -> None:
    resource_manager.setup_window_icon(window)

# Instâncias globais úteis
theme_manager = ThemeManager()
resource_manager = ResourceManager()
ui_helper = UIHelper()