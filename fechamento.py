import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_LABEL, FONT_ENTRY
from utils import setup_window_icon
from lojas import lojas

class EmailGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.logger = AustralLogger()

        # Configurações iniciais
        self.lojas_lista = [loja["loja"] for loja in lojas]
        self.filial_var = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.nome_var = tk.StringVar()

        # Configura a interface do usuário
        self.setup_ui()
        setup_window_icon(self.root)
        self.load_last_values()

    def center_window(self):
        """Centraliza a janela na tela"""
        # Atualiza a janela para garantir que ela tenha as dimensões corretas
        self.root.update_idletasks()
        
        # Obtém as dimensões da tela e da janela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500  # Largura que definimos na geometria
        window_height = 200 # Altura que definimos na geometria
        
        # Calcula a posição x e y para centralizar
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Define a nova geometria da janela
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def validar_campos(self):
        """Valida os campos antes de gerar o email"""
        if not self.filial_var.get():
            messagebox.showwarning("ATENÇÃO", "Selecione uma filial!")
            return False

        if not self.valor_var.get():
            messagebox.showwarning("ATENÇÃO", "Digite o valor total!")
            return False

        if not self.nome_var.get().strip():
            messagebox.showwarning("ATENÇÃO", "Digite seu nome!")
            return False

        return True

    @log_action("generate_email")
    def gerar_email(self):
        """Gera o email e mostra em uma nova janela"""
        if not self.validar_campos():
            return

        try:
            # Prepara os dados para o email
            filial = self.filial_var.get()
            
            # Converte o valor para formato brasileiro
            try:
                valor = float(self.valor_var.get().replace(',','.'))
                valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                messagebox.showerror("ERRO", "Valor inválido! Use apenas números e virgula. Para R$15.000,00 digite 15000,00!")
                return
                
            nome = self.nome_var.get().strip()
            data_atual = datetime.now().strftime("%d/%m/%Y")

            # Cria o corpo do email com as informações fornecidas
            email_body = (
                f"Boa noite,\n\n"
                f"Segue o resumo do fechamento do dia {data_atual} "
                f"da filial {filial}:\n\n"
                f"VALOR TOTAL VENDIDO: R$ {valor_formatado}\n\n"
                "Em anexo você encontrará o FECHAMENTO DETALHADO e "
                "o ACUMULADO DIÁRIO, ambos referente ao dia.\n\n\n"
                f"Atenciosamente,\n"
                f"{nome}"
            )

            # Cria uma nova janela para exibir o email gerado
            preview_window = ttk.Toplevel(self.root)
            preview_window.title("E-MAIL GERADO")
            preview_window.geometry("500x350")
            preview_window.minsize(500, 350)

            # Cria um container principal para a janela de preview
            main_container = ttk.Frame(preview_window)
            main_container.pack(fill=tk.BOTH, expand=True)

            # Cria uma área de texto para exibir o email
            text_area = tk.Text(
                main_container,
                font=("Helvetica", 10),
                wrap=tk.WORD,
                padx=10,
                pady=10,
                height=15
            )
            text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text_area.insert('1.0', email_body)
            text_area.config(state='disabled')

            # Cria um frame para o botão de copiar
            button_frame = ttk.Frame(main_container, height=50)
            button_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
            button_frame.pack_propagate(False)

            # Cria um botão para copiar o email para a área de transferência
            copy_button = ttk.Button(
                button_frame,
                text="COPIAR E-MAIL",
                command=lambda: self.copiar_email(email_body, preview_window),
                style="Info.TButton",
                width=40
            )
            copy_button.place(relx=0.5, rely=0.5, anchor="center")

            # Salva os valores usados para uso futuro
            self.save_last_values()

        except Exception as e:
            messagebox.showerror(
                "ERRO",
                f"Erro ao gerar e-mail: {str(e)}"
            )

    def copiar_email(self, email_body, window):
        """Copia o email para a área de transferência e fecha a janela"""
        self.root.clipboard_clear()
        self.root.clipboard_append(email_body)
        messagebox.showinfo(
            "SUCESSO",
            "E-mail copiado para área de transferência!"
        )
        window.destroy()

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.filial_var.set('')
        self.valor_var.set('')
        self.nome_var.set('')

    def save_last_values(self):
        """Salva os últimos valores utilizados"""
        self.config.set('email_generator.last_values', {
            'filial': self.filial_var.get(),
            'nome': self.nome_var.get()
        })

    def load_last_values(self):
        """Carrega os últimos valores utilizados"""
        last_values = self.config.get('email_generator.last_values', {})
        if last_values:
            self.filial_var.set(last_values.get('filial', ''))
            self.nome_var.set(last_values.get('nome', ''))

    def setup_ui(self):
        """Configura a interface do gerador de e-mail de forma compacta"""
        # Cria um frame principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Cria um frame para entrada de dados com uma borda e título
        input_frame = ttk.LabelFrame(
            main_frame,
            text="DADOS DO FECHAMENTO",
            padding="5"
        )
        input_frame.pack(fill=tk.X, pady=(0, 5))

        # Configura o layout de colunas do frame de entrada
        input_frame.columnconfigure(1, weight=1)

        # Campo FILIAL
        ttk.Label(
            input_frame,
            text="FILIAL:",
            font=("Helvetica", 10)
        ).grid(row=0, column=0, sticky='w', padx=2, pady=2)

        self.filial_combo = ttk.Combobox(
            input_frame,
            textvariable=self.filial_var,
            values=self.lojas_lista,
            font=("Helvetica", 10),
            width=35,
            state="readonly"
        )
        self.filial_combo.grid(row=0, column=1, sticky='ew', padx=2, pady=2)

        # Campo VALOR TOTAL
        ttk.Label(
            input_frame,
            text="VALOR TOTAL:",
            font=("Helvetica", 10)
        ).grid(row=1, column=0, sticky='w', padx=2, pady=2)

        self.valor_entry = ttk.Entry(
            input_frame,
            textvariable=self.valor_var,
            font=("Helvetica", 10),
            width=35
        )
        self.valor_entry.grid(row=1, column=1, sticky='ew', padx=2, pady=2)

        # Campo SEU NOME
        ttk.Label(
            input_frame,
            text="SEU NOME:",
            font=("Helvetica", 10)
        ).grid(row=2, column=0, sticky='w', padx=2, pady=2)

        self.nome_entry = ttk.Entry(
            input_frame,
            textvariable=self.nome_var,
            font=("Helvetica", 10),
            width=35
        )
        self.nome_entry.grid(row=2, column=1, sticky='ew', padx=2, pady=2)

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Botão LIMPAR
        ttk.Button(
            button_frame,
            text="LIMPAR",
            command=self.limpar_campos,
            style="danger.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=2)

        # Botão GERAR E-MAIL
        ttk.Button(
            button_frame,
            text="GERAR E-MAIL",
            command=self.gerar_email,
            style="Info.TButton",
            width=12
        ).pack(side=tk.RIGHT, padx=2)

        # Define o tamanho da janela e centraliza
        self.root.geometry("500x200")
        self.center_window()

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    root.title("E-MAIL DE FECHAMENTO AUSTRAL")
    app = EmailGeneratorApp(root)
    root.mainloop()
