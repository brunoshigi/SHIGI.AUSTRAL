import os
from pathlib import Path
import tkinter as tk

class ResourceManager:
    def __init__(self):
        # Define o diretório base como a raiz do projeto
        self.base_path = Path(__file__).parent

    def get_resource_path(self, filename: str) -> Path:
        """
        Retorna o caminho absoluto para um recurso na raiz do projeto.

        Args:
            filename: Nome do arquivo do recurso.

        Returns:
            Path: Caminho absoluto para o recurso.
        """
        resource_path = self.base_path / filename

        if not resource_path.exists():
            raise FileNotFoundError(f"Recurso não encontrado: {filename}")

        return resource_path

    def setup_window_icon(self, window: tk.Tk) -> None:
        """
        Configura o ícone da janela principal.

        Args:
            window: Instância da janela tkinter.
        """
        try:
            icon_path = self.get_resource_path('icone.ico')  # Ícone na raiz do projeto
            if os.name == 'nt':  # Windows
                window.iconbitmap(default=str(icon_path))
            else:  # Linux/Mac
                icon = tk.PhotoImage(file=str(icon_path))
                window.iconphoto(True, icon)
        except Exception as e:
            print(f"Erro ao configurar ícone: {e}")

    def cleanup_temp(self, temp_dir: str, max_age_days: int = 7) -> None:
        """
        Limpa arquivos temporários mais antigos que max_age_days.

        Args:
            temp_dir: Caminho para o diretório temporário.
            max_age_days: Tempo máximo permitido, em dias.
        """
        temp_path = Path(temp_dir)
        cutoff_time = (Path.cwd().stat().st_ctime - (max_age_days * 86400))
        for file in temp_path.iterdir():
            if file.stat().st_ctime < cutoff_time:
                file.unlink()


# Instância global do gerenciador de recursos
resource_manager = ResourceManager()
