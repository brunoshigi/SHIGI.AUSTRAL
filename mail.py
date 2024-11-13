import tkinter as tk  # Importa o módulo tkinter para criar interfaces gráficas
from tkinter import messagebox  # Importa messagebox para exibir diálogos de mensagem
import ttkbootstrap as ttk  # Importa ttkbootstrap para estilos modernos no tkinter
from ttkbootstrap.constants import *  # Importa constantes usadas no ttkbootstrap
from datetime import datetime  # Importa datetime para manipular datas e horários
from config import ConfigManager  # Importa o gerenciador de configurações personalizadas
from logger import AustralLogger, log_action  # Importa o logger personalizado e decorador de log
from utils import FONT_LABEL, FONT_ENTRY  # Importa fontes personalizadas para labels e entradas
from utils import setup_window_icon  # Importa função para configurar o ícone da janela
from lojas import lojas  # Importa a lista de lojas do arquivo lojas.py

# Define a classe principal do aplicativo
class EmailGeneratorApp:
    def __init__(self, root):
        self.root = root  # Armazena a referência da janela principal
        self.config = ConfigManager()  # Instancia o gerenciador de configurações
        self.logger = AustralLogger()  # Instancia o logger para registrar ações

        # Configura a interface do usuário
        self.setup_ui()
        setup_window_icon(self.root)  # Configura o ícone da janela principal
        self.load_last_values()  # Carrega os últimos valores utilizados

    def setup_ui(self):
        """Configura a interface do gerador de e-mail de forma compacta"""
        # Cria um frame principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)  # Adiciona o frame à janela principal

        # Cria um frame para entrada de dados com uma borda e título
        input_frame = ttk.LabelFrame(
            main_frame,
            text="DADOS DO FECHAMENTO",
            padding="5"
        )
        input_frame.pack(fill=tk.X, pady=(0, 5))  # Adiciona o frame ao frame principal

        # Configura o layout de colunas do frame de entrada
        input_frame.columnconfigure(1, weight=1)

        # Cria um label para o campo "FILIAL"
        ttk.Label(
            input_frame,
            text="FILIAL:",
            font=("Helvetica", 10)
        ).grid(row=0, column=0, sticky='w', padx=2, pady=2)  # Posiciona o label no grid

        # Obtém a lista de lojas do arquivo lojas.py
        self.lojas_lista = [loja["loja"] for loja in lojas]
        self.filial_var = tk.StringVar()  # Cria uma variável para armazenar a filial selecionada

        # Cria um combobox para selecionar a filial
        self.filial_combo = ttk.Combobox(
            input_frame,
            textvariable=self.filial_var,  # Associa a variável ao combobox
            values=self.lojas_lista,  # Define as opções do combobox com a lista de lojas
            font=("Helvetica", 10),
            width=35,
            state="readonly"  # Impede que o usuário digite valores não listados
        )
        self.filial_combo.grid(row=0, column=1, sticky='ew', padx=2, pady=2)  # Posiciona o combobox

        # Cria um label para o campo "VALOR TOTAL"
        ttk.Label(
            input_frame,
            text="VALOR TOTAL:",
            font=("Helvetica", 10)
        ).grid(row=1, column=0, sticky='w', padx=2, pady=2)  # Posiciona o label

        self.valor_var = tk.StringVar()  # Cria uma variável para armazenar o valor total

        # Cria um entry para inserir o valor total
        self.valor_entry = ttk.Entry(
            input_frame,
            textvariable=self.valor_var,  # Associa a variável ao entry
            font=("Helvetica", 10),
            width=35
        )
        self.valor_entry.grid(row=1, column=1, sticky='ew', padx=2, pady=2)  # Posiciona o entry

        # Configura um trace para formatar o valor enquanto o usuário digita
        self.valor_var.trace('w', self.format_valor)

        # Cria um label para o campo "SEU NOME"
        ttk.Label(
            input_frame,
            text="SEU NOME:",
            font=("Helvetica", 10)
        ).grid(row=2, column=0, sticky='w', padx=2, pady=2)  # Posiciona o label

        self.nome_var = tk.StringVar()  # Cria uma variável para armazenar o nome do usuário

        # Cria um entry para inserir o nome do remetente
        self.nome_entry = ttk.Entry(
            input_frame,
            textvariable=self.nome_var,  # Associa a variável ao entry
            font=("Helvetica", 10),
            width=35
        )
        self.nome_entry.grid(row=2, column=1, sticky='ew', padx=2, pady=2)  # Posiciona o entry

        # Cria um frame para os botões com padding reduzido
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)  # Adiciona o frame de botões

        # Cria o botão "LIMPAR" para limpar os campos
        ttk.Button(
            button_frame,
            text="LIMPAR",
            command=self.limpar_campos,  # Associa a função de limpar campos
            style="Secondary.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=2)  # Posiciona o botão à esquerda

        # Cria o botão "GERAR E-MAIL" para gerar o email
        ttk.Button(
            button_frame,
            text="GERAR E-MAIL",
            command=self.gerar_email,  # Associa a função de gerar email
            style="Primary.TButton",
            width=12
        ).pack(side=tk.RIGHT, padx=2)  # Posiciona o botão à direita

        # Define um tamanho inicial mais compacto para a janela principal
        self.root.geometry("500x200")

    def format_valor(self, *args):
        """Formata o valor enquanto o usuário digita"""
        valor = self.valor_var.get().replace('.', '').replace(',', '')  # Remove pontos e vírgulas
        valor = ''.join(filter(str.isdigit, valor))  # Mantém apenas dígitos numéricos

        if valor:
            try:
                # Converte para float, considerando centavos
                valor_float = float(valor) / 100 if len(valor) > 2 else float(valor)

                # Remove o trace atual para evitar chamadas recursivas
                self.valor_var.trace_vdelete('w', self.valor_var.trace_info()[0][1])

                # Formata o valor com vírgula e duas casas decimais (formato brasileiro)
                valor_formatado = f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.valor_var.set(valor_formatado)  # Atualiza o valor formatado no entry

                # Recoloca o trace para continuar monitorando mudanças
                self.valor_var.trace('w', self.format_valor)
            except ValueError:
                pass  # Ignora erros caso a conversão falhe

    @log_action("generate_email")  # Decora a função para registrar a ação de gerar email
    def gerar_email(self):
        """Gera o email e mostra em uma nova janela"""
        if not self.validar_campos():
            return  # Se a validação falhar, interrompe a execução

        try:
            # Prepara os dados para o email
            filial = self.filial_var.get()  # Obtém a filial selecionada
            valor_str = self.valor_var.get().replace('.', '').replace(',', '')  # Remove pontos e vírgulas
            valor = float(valor_str) / 100  # Converte o valor para float
            nome = self.nome_var.get().strip()  # Obtém o nome do remetente
            data_atual = datetime.now().strftime("%d/%m/%Y")  # Formata a data atual

            # Formata o valor para exibição no email
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Cria o corpo do email com as informações fornecidas
            email_body = (
                f"Boa noite,\n\n"
                f"Segue o resumo do fechamento do dia {data_atual} "
                f"da filial {filial}:\n\n"
                f"VALOR TOTAL VENDIDO: R$ {valor_formatado}\n\n"
                "Em anexo você encontrará o fechamento detalhado e "
                "o inventário de vendas, ambos referente ao dia.\n\n\n"
                f"Atenciosamente,\n"
                f"{nome}"
            )

            # Cria uma nova janela para exibir o email gerado
            preview_window = ttk.Toplevel(self.root)
            preview_window.title("E-MAIL GERADO")  # Define o título da janela
            preview_window.geometry("500x350")  # Define o tamanho da janela
            preview_window.minsize(500, 350)  # Define o tamanho mínimo da janela

            # Cria um container principal para a janela de preview
            main_container = ttk.Frame(preview_window)
            main_container.pack(fill=tk.BOTH, expand=True)  # Expande o frame para preencher a janela

            # Cria uma área de texto para exibir o email
            text_area = tk.Text(
                main_container,
                font=("Helvetica", 10),
                wrap=tk.WORD,  # Quebra de linha automática
                padx=10,
                pady=10,
                height=15  # Altura em linhas
            )
            text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Adiciona a área de texto
            text_area.insert('1.0', email_body)  # Insere o corpo do email na área de texto
            text_area.config(state='disabled')  # Define a área de texto como somente leitura

            # Cria um frame para o botão de copiar
            button_frame = ttk.Frame(main_container, height=50)  # Altura definida
            button_frame.pack(fill=tk.X, pady=(0, 5), padx=5)
            button_frame.pack_propagate(False)  # Impede que o frame mude de tamanho

            # Cria um botão para copiar o email para a área de transferência
            copy_button = ttk.Button(
                button_frame,
                text="COPIAR PARA ÁREA DE TRANSFERÊNCIA",
                command=lambda: self.copiar_email(email_body, preview_window),  # Associa a função
                style="Primary.TButton",
                width=40  # Largura aumentada
            )
            copy_button.place(relx=0.5, rely=0.5, anchor="center")  # Centraliza o botão no frame

            # Salva os valores usados para uso futuro
            self.save_last_values()

        except Exception as e:
            # Exibe uma mensagem de erro caso ocorra uma exceção
            messagebox.showerror(
                "ERRO",
                f"Erro ao gerar e-mail: {str(e)}"
            )

    def validar_campos(self) -> bool:
        """Valida os campos antes de gerar o email"""
        if not self.filial_var.get():
            messagebox.showwarning("ATENÇÃO", "Selecione uma filial!")  # Alerta se a filial não for selecionada
            return False

        if not self.valor_var.get():
            messagebox.showwarning("ATENÇÃO", "Digite o valor total!")  # Alerta se o valor não for digitado
            return False

        if not self.nome_var.get().strip():
            messagebox.showwarning("ATENÇÃO", "Digite seu nome!")  # Alerta se o nome não for digitado
            return False

        return True  # Todos os campos estão válidos

    def copiar_email(self, email_body: str, window: ttk.Toplevel):
        """Copia o email para a área de transferência e fecha a janela"""
        self.root.clipboard_clear()  # Limpa a área de transferência
        self.root.clipboard_append(email_body)  # Copia o corpo do email para a área de transferência
        messagebox.showinfo(
            "SUCESSO",
            "E-mail copiado para área de transferência!"
        )
        window.destroy()  # Fecha a janela de preview

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.filial_var.set('')  # Limpa a seleção da filial
        self.valor_var.set('')  # Limpa o valor total
        self.nome_var.set('')  # Limpa o nome do usuário

    def save_last_values(self):
        """Salva os últimos valores utilizados"""
        # Salva a filial e o nome nos dados de configuração
        self.config.set('email_generator.last_values', {
            'filial': self.filial_var.get(),
            'nome': self.nome_var.get()
        })

    def load_last_values(self):
        """Carrega os últimos valores utilizados"""
        # Obtém os últimos valores salvos
        last_values = self.config.get('email_generator.last_values', {})
        if last_values:
            self.filial_var.set(last_values.get('filial', ''))  # Define a filial
            self.nome_var.set(last_values.get('nome', ''))  # Define o nome do usuário

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    root = ttk.Window(themename="litera")  # Cria a janela principal com o tema 'litera'
    root.title("GERADOR DE E-MAIL - FECHAMENTO")  # Define o título da janela
    app = EmailGeneratorApp(root)  # Instancia a aplicação principal
    root.mainloop()  # Inicia o loop principal da interface gráfica
