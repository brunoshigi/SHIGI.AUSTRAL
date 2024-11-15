# test_resources.py
import os
from pathlib import Path
from PIL import Image

def check_resources():
    """Verifica se os recursos existem e podem ser carregados"""
    base_path = Path(__file__).parent
    assets_path = base_path / 'assets'
    
    print("\nVerificando recursos...")
    print("-" * 50)
    
    # Verifica a pasta assets
    if not assets_path.exists():
        print(f"❌ Pasta assets não encontrada em: {assets_path}")
        return
    print(f"✅ Pasta assets encontrada em: {assets_path}")
    
    # Verifica logo_nome.png
    logo_path = assets_path / 'logo_nome.png'
    if logo_path.exists():
        print(f"✅ logo_nome.png encontrado")
        try:
            logo = Image.open(logo_path)
            print(f"  └ Dimensões: {logo.size}")
            print(f"  └ Modo: {logo.mode}")
            print(f"  └ Formato: {logo.format}")
        except Exception as e:
            print(f"❌ Erro ao abrir logo_nome.png: {e}")
    else:
        print(f"❌ logo_nome.png não encontrado em: {logo_path}")
    
    # Verifica icone.ico
    icon_path = assets_path / 'icone.ico'
    if icon_path.exists():
        print(f"✅ icone.ico encontrado")
        try:
            icon = Image.open(icon_path)
            print(f"  └ Dimensões: {icon.size}")
            print(f"  └ Modo: {icon.mode}")
            print(f"  └ Formato: {icon.format}")
        except Exception as e:
            print(f"❌ Erro ao abrir icone.ico: {e}")
    else:
        print(f"❌ icone.ico não encontrado em: {icon_path}")

if __name__ == "__main__":
    check_resources()