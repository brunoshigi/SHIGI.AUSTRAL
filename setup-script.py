import PyInstaller.__main__
import os
from pathlib import Path
import sys
import shutil

def create_executable():
    """
    Cria o executável do sistema Austral
    """
    # Diretório base do projeto
    base_dir = Path(__file__).parent.resolve()
    
    # Nome do arquivo principal
    main_script = base_dir / 'main.py'
    
    # Diretório de recursos (raiz do projeto)
    resource_dir = base_dir
    
    # Limpar diretório dist e build se existirem
    for dir_name in ['dist', 'build']:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    # Arquivos de recursos e suas pastas destino
    resources = []
    for root, dirs, files in os.walk(resource_dir):
        for file in files:
            if file.endswith(('.py', '.pyc', '.spec')):
                continue
            file_path = Path(root) / file
            relative_path = file_path.relative_to(base_dir)
            resources.append((str(file_path), '.'))  # Inclui diretamente na raiz
    
    # Inclui outros recursos necessários
    additional_dirs = ['templates', 'config', 'data']
    for dir_name in additional_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(base_dir)
                    resources.append((str(file_path), '.'))
    
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
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ]
    
    # Configurações do PyInstaller
    PyInstaller.__main__.run([
        str(main_script),
        '--name=Austral',
        '--onefile',
        '--windowed',
        f'--icon={base_dir / "icone.ico"}',
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

    print("\nExecutável criado com sucesso!")
    print(f"Localização: {base_dir / 'dist' / 'Austral.exe'}")

if __name__ == "__main__":
    try:
        create_executable()
    except Exception as e:
        print(f"Erro ao criar executável: {e}")
        sys.exit(1)