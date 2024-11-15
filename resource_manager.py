import os
import sys
from pathlib import Path
import shutil

class ResourceManager:
    def __init__(self):
        # Define o diretório base baseado se é executável ou script
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent.parent

        # Define os diretórios principais
        self.assets_dir = self.base_path / 'assets'
        self.data_dir = self.base_path / 'data'
        self.logs_dir = self.base_path / 'logs'
        self.temp_dir = self.base_path / 'temp'

        # Cria os diretórios necessários
        self.ensure_directories()

    def ensure_directories(self):
        """Garante que todos os diretórios necessários existam"""
        dirs = [
            self.assets_dir,
            self.data_dir,
            self.logs_dir,
            self.temp_dir
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_resource_path(self, resource_name: str) -> Path:
        """
        Retorna o caminho absoluto para um recurso
        """
        if getattr(sys, 'frozen', False):
            # Se for executável, procura no diretório temporário do PyInstaller
            resource_path = self.base_path / 'assets' / resource_name
        else:
            # Se for script, procura no diretório do projeto
            resource_path = self.assets_dir / resource_name

        if not resource_path.exists():
            raise FileNotFoundError(f"Recurso não encontrado: {resource_name}")

        return resource_path

    def get_data_path(self) -> Path:
        """Retorna o caminho para o diretório de dados"""
        return self.data_dir

    def get_logs_path(self) -> Path:
        """Retorna o caminho para o diretório de logs"""
        return self.logs_dir

    def get_temp_path(self) -> Path:
        """Retorna o caminho para o diretório temporário"""
        return self.temp_dir

    def cleanup_temp(self, max_age_days: int = 7):
        """Limpa arquivos temporários mais antigos que max_age_days"""
        now = Path.ctime(Path())
        for file in self.temp_dir.glob('*'):
            if (now - Path.ctime(file)).days > max_age_days:
                file.unlink()

# Instância global do gerenciador de recursos
resource_manager = ResourceManager()