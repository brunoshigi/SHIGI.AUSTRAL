"""
Adicione esta função no início dos arquivos delivery.py e transfer.py:
"""

import os
import sys
from pathlib import Path

def get_resource_path(filename: str) -> str:
    """
    Retorna o caminho correto para um recurso, seja em desenvolvimento ou no executável
    """
    try:
        # Se estiver rodando como executável PyInstaller
        if getattr(sys, '_MEIPASS', False):
            return os.path.join(sys._MEIPASS, 'assets', filename)
        
        # Se estiver rodando como script
        base_path = Path(__file__).resolve().parent
        
        # Procura em possíveis localizações
        possible_paths = [
            base_path / 'assets' / filename,           # ./assets/file
            base_path / filename,                      # ./file
            base_path.parent / 'assets' / filename,    # ../assets/file
            base_path.parent / filename                # ../file
        ]
        
        # Retorna o primeiro caminho válido
        for path in possible_paths:
            if path.exists():
                return str(path)
                
        # Se não encontrou, procura na pasta do executável
        if hasattr(sys, 'frozen'):
            return os.path.join(os.path.dirname(sys.executable), 'assets', filename)
            
        return None
        
    except Exception as e:
        print(f"Erro ao localizar recurso {filename}: {e}")
        return None

"""
Então modifique o código de carregamento do logo em ambos os arquivos:
"""

# Em delivery.py e transfer.py, substitua:
try:
    logo = Image.open("logo_nome.png")
    # ...
except Exception as e:
    # ...

# Por:
try:
    logo_path = get_resource_path("logo_nome.png")
    if logo_path:
        logo = Image.open(logo_path)
        # ... resto do código ...
    else:
        UIHelper.show_message(
            "AVISO",
            "Logo não encontrado. Usando texto como alternativa.",
            "warning"
        )
        draw.text((self.MARGEM, y), "Austral", font=fonte_titulo, fill="black")
        y += 50
except Exception as e:
    UIHelper.show_message(
        "AVISO",
        f"Erro ao carregar logo: {str(e)}. Usando texto como alternativa.",
        "warning"
    )
    draw.text((self.MARGEM, y), "Austral", font=fonte_titulo, fill="black")
    y += 50