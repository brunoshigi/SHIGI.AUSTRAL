import PyInstaller.__main__
import os
from pathlib import Path
import sys

def create_executable():
    """
    Cria o executável do sistema Austral
    """
    # Diretório base do projeto
    base_dir = Path(__file__).parent.resolve()
    
    # Nome do arquivo principal
    main_script = base_dir / 'main.py'
    
    # Diretório de recursos
    resource_dir = base_dir / 'assets'
    
    # Verifica se o diretório de recursos existe
    if not resource_dir.exists():
        print(f"Diretório de recursos não encontrado: {resource_dir}")
        sys.exit(1)
    
    # Arquivos de recursos e suas pastas destino
    resources = []
    for root, dirs, files in os.walk(resource_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(base_dir)
            resources.append((str(file_path), str(relative_path.parent)))
    
    # Inclui outros recursos necessários (exemplo: templates, configurações)
    additional_dirs = ['templates', 'config', 'data']
    for dir_name in additional_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(base_dir)
                    resources.append((str(file_path), str(relative_path.parent)))
    
    # Lista de dados adicionais formatada conforme o sistema operacional
    if os.name == 'nt':  # Windows
        datas = [f"{f[0]};{f[1]}" for f in resources]
    else:  # Linux/Mac
        datas = [f"{f[0]}:{f[1]}" for f in resources]
    
    # Dependências ocultas que precisam ser incluídas
    hidden_imports = [
        'ttkbootstrap',
        'PIL',
        'PIL._tkinter_finder',
        'sqlite3',
        'pandas',
        'openpyxl',
        'requests',
        'babel.numbers',
        'ttkbootstrap.icons',
        'babel',
        'babel.numbers',
        'babel.core',
    ]
    
    # Configurações do PyInstaller
    PyInstaller.__main__.run([
        str(main_script),
        '--name=Austral',
        '--onefile',
        '--windowed',
        f'--icon={resource_dir / "icone.ico"}',
        '--clean',
        '--noconsole',
        *[f'--add-data={data}' for data in datas],
        *[f'--hidden-import={imp}' for imp in hidden_imports],
        '--uac-admin',  # Solicita elevação de privilégios no Windows
        '--collect-all=ttkbootstrap',
        '--collect-all=babel',
        '--copy-metadata=ttkbootstrap',
        '--copy-metadata=babel',
        '--noupx',
        '--exclude-module=PyQt5',
        '--exclude-module=PyQt6',
        '--exclude-module=PySide2',
        '--exclude-module=PySide6',
    ])

if __name__ == "__main__":
    create_executable()
