# main.py
from ttkbootstrap import Window
from system import AustralSystem
import sys

def main():
    try:
        root = Window()
        app = AustralSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Erro crítico ao iniciar sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()