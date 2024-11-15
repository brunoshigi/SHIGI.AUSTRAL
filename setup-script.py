import PyInstaller.__main__
import os
from pathlib import Path

def create_executable():
    """
    Cria o executável do sistema Austral
    """
    # Diretório base do projeto
    base_dir = Path(__file__).parent
    
    # Nome do arquivo principal
    main_script = base_dir / 'main.py'
    
    # Diretório de recursos
    resource_dir = base_dir / 'assets'
    resource_dir.mkdir(exist_ok=True)
    
    # Arquivos de recursos e suas pastas destino
    resources = [
        (resource_dir / 'logo_nome.png', 'assets'),
        (resource_dir / 'icone.ico', 'assets')
    ]
    
    # Lista de dados adicionais formatada conforme o sistema operacional
    if os.name == 'nt':  # Windows
        datas = [f"{str(f[0])};{f[1]}" for f in resources]
    else:  # Linux/Mac
        datas = [f"{str(f[0])}:{f[1]}" for f in resources]
    
    # Dependências ocultas que precisam ser incluídas
    hidden_imports = [
        'ttkbootstrap',
        'PIL',
        'PIL._tkinter_finder',
        'sqlite3',
        'pandas',
        'openpyxl',
        'requests',
        'babel.numbers'
    ]
    
    # Configurações do PyInstaller
    PyInstaller.__main__.run([
        str(main_script),
        '--name=Austral',
        '--onefile',
        '--windowed',
        f'--icon={resource_dir}/icone.ico',
        '--clean',
        '--noconsole',
        *[f'--add-data={data}' for data in datas],
        *[f'--hidden-import={imp}' for imp in hidden_imports],
        '--uac-admin',  # Solicita elevação de privilégios no Windows
        '--collect-all=ttkbootstrap',
        '--collect-all=babel',
        '--copy-metadata=ttkbootstrap',
        '--noupx'
    ])

if __name__ == "__main__":
    create_executable()