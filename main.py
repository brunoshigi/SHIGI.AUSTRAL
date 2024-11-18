# main.py
from ttkbootstrap import Window
from system import AustralSystem
import sys
from config import ConfigManager

def main():
    try:
        config = ConfigManager()
        config.setup_all_databases()

        root = Window()
        app = AustralSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro crítico ao iniciar sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()