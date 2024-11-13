import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY, SECONDARY

import pandas as pd
from datetime import datetime
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_LABEL, FONT_ENTRY, FONT_TITLE
import os
from utils import UIHelper


user_diretorio = os.path.expanduser('~')

user_diretorio = user_diretorio.replace("\\",'/')

class MixDiarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIX DIÁRIO - AUSTRAL")
        self.config = ConfigManager()
        self.logger = AustralLogger()

        # Mapeamento de nomes de lojas para códigos de filiais
        self.branch_codes = {
            "AUSTRAL IGUATEMI SP": "000002",
            "AUSTRAL HIGIENÓPOLIS": "000003",
            "AUSTRAL MORUMBI": "000012",
            "AUSTRAL CATARINA FASHION OUTLET": "000014",
            "AUSTRAL IGUATEMI ALPHAVILLE": "000015",
            "AUSTRAL SHOPPING JK IGUATEMI": "000016"
        }

        # Lista para armazenar os códigos
        self.codigos = []

        # Variável para armazenar a última atualização
        self.last_update = self.config.get('mix_diario.last_update', 'NENHUMA')

        # Caminho para o arquivo Excel
        self.excel_file_path = self.config.get('mix_diario.excel_file_path', 'mix_diario.xlsx')

        # Configuração da janela
        self.setup_ui()

        # Carregar dados temporários (sem selecionar a loja)
        self.load_temp_data()

        # Foco inicial no campo de código
        self.codigo_entry.focus()

    def setup_ui(self):
        """Configura a interface do Mix Diário"""
        # Definir tamanho fixo da janela
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Container principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de seleção de loja e entrada de código
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        # Configuração das colunas no grid
        top_frame.columnconfigure(0, weight=0)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=0)
        top_frame.columnconfigure(3, weight=0)
        top_frame.columnconfigure(4, weight=0)

        # Combobox de seleção de loja
        loja_label = ttk.Label(
            top_frame,
            text="LOJA:",
            font=FONT_LABEL
        )
        loja_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky=tk.W)

        self.loja_var = tk.StringVar()
        self.loja_combo = ttk.Combobox(
            top_frame,
            textvariable=self.loja_var,
            values=list(self.branch_codes.keys()),
            font=FONT_ENTRY,
            width=25,
            state="readonly"
        )
        self.loja_combo.grid(row=0, column=1, padx=(0, 10), pady=5, sticky=tk.W)
        self.loja_combo.set('')  # Combobox vazia no início

        # Campo de entrada do código
        codigo_label = ttk.Label(
            top_frame,
            text="SKU:",
            font=FONT_LABEL
        )
        codigo_label.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.W)

        self.codigo_entry = ttk.Entry(
            top_frame,
            font=FONT_ENTRY,
            width=20
        )
        self.codigo_entry.grid(row=0, column=3, padx=(0, 5), pady=5, sticky=tk.W)
        self.codigo_entry.bind("<Return>", self.registrar_codigo)

        # Botão para registrar código
        registrar_button = ttk.Button(
            top_frame,
            text="REGISTRAR",
            command=self.registrar_codigo,
            style="Primary.TButton"
        )
        registrar_button.grid(row=0, column=4, padx=(5, 0), pady=5, sticky=tk.W)

        # Frame para a tabela de códigos
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Configuração da Treeview
        columns = ("data", "hora", "filial", "sku")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=20
        )

        # Definir cabeçalhos das colunas
        self.tree.heading("data", text="DATA")
        self.tree.heading("hora", text="HORA")
        self.tree.heading("filial", text="FILIAL")
        self.tree.heading("sku", text="SKU")

        # Definir largura das colunas
        self.tree.column("data", width=80, anchor='center')
        self.tree.column("hora", width=60, anchor='center')
        self.tree.column("filial", width=60, anchor='center')
        self.tree.column("sku", width=200, anchor='center')

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical para a Treeview
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # Espaçamento entre botões
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        # Botão para remover último código
        remover_button = ttk.Button(
            button_frame,
            text="REMOVER ÚLTIMO",
            command=self.remover_ultimo,
            style="danger.TButton"
        )
        remover_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)

        # Botão para limpar tudo
        limpar_button = ttk.Button(
            button_frame,
            text="LIMPAR TUDO",
            command=self.limpar_tudo,
            style="Warning.TButton" 
        )
        limpar_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # Botão para finalizar
        atualizar_button = ttk.Button(
            button_frame,
            text="ATUALIZAR ARQUIVO",
            command=self.finalizar_mix, 
            style="Primar.TButton"
        )
        atualizar_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)

        # Label para última atualização
        self.last_update_label = ttk.Label(
            main_frame,
            text=f"ÚLTIMA ATUALIZAÇÃO: {self.last_update}",
            font=FONT_LABEL, 
            foreground="red"
        )
        self.last_update_label.pack(pady=(5, 0), anchor=tk.E)

    @log_action("register_code")
    def registrar_codigo(self, event=None):
        """Registra um novo código na lista"""
        codigo = self.codigo_entry.get().strip()

        if not self.loja_var.get():
            messagebox.showwarning("ATENÇÃO", "SELECIONE UMA LOJA PRIMEIRO!")
            return

        if not codigo:
            return

        # Obtém a data e hora atuais
        now = datetime.now()
        date_str = now.strftime('%d/%m/%Y')
        time_str = now.strftime('%H:%M:%S')

        # Obtém o código da filial
        branch_code = self.branch_codes.get(self.loja_var.get(), 'DESCONHECIDO')

        # Adiciona os dados à lista
        new_entry = {
            'data': date_str,
            'hora': time_str,
            'filial': branch_code,
            'sku': codigo
        }
        self.codigos.append(new_entry)

        # Atualiza a interface
        self.tree.insert('', 'end', values=(date_str, time_str, branch_code, codigo))
        self.codigo_entry.delete(0, tk.END)

        # Salva o progresso
        self.save_progress()

    def remover_ultimo(self):
        """Remove o último código registrado"""
        if self.codigos:
            self.codigos.pop()
            items = self.tree.get_children()
            if items:
                self.tree.delete(items[-1])
            self.save_progress()

    def limpar_tudo(self):
        """Limpa todos os códigos registrados"""
        if messagebox.askyesno("CONFIRMAR", "DESEJA REALMENTE LIMPAR TODOS OS CÓDIGOS?"):
            self.codigos.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.save_progress()

    @log_action("generate_mix_report")
    def finalizar_mix(self):
        """Atualiza o arquivo Excel existente com os novos dados"""
        if not self.codigos:
            messagebox.showwarning("ATENÇÃO", "NENHUM CÓDIGO REGISTRADO!")
            return

        if not self.loja_var.get():
            messagebox.showwarning("ATENÇÃO", "SELECIONE UMA LOJA!")
            return

        try:
            # Cria um DataFrame com os novos dados
            df_new = pd.DataFrame(self.codigos)

            # Tenta ler o arquivo existente
            try:
                filial = self.branch_codes.get(self.loja_var.get(), 'DESCONHECIDO')
                if filial == "000002":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - lojaiguatemi/Mix diário/{self.excel_file_path}')
                elif filial == "000003":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Pátio Higienópolis/Mix diário/{self.excel_file_path}')
                elif filial == "000014":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - lojaiguatemi/Mix diário/{self.excel_file_path}')
                elif filial == "000015":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Iguatemi Alphaville/Mix diário/{self.excel_file_path}')
                elif filial == "000016":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja JK Iguatemi/Mix diário/{self.excel_file_path}')
                elif filial == "000012":
                    df_existing = pd.read_excel(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Morumbi/Mix diário/{self.excel_file_path}')
                else:
                    print('Filial desconhecida')
            except FileNotFoundError:
                df_existing = pd.DataFrame(columns=['data', 'hora', 'filial', 'sku'])

            # Concatena os dados existentes com os novos
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)

            # Salva no arquivo
            if filial == "000002":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - lojaiguatemi/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            elif filial == "000003":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Pátio Higienópolis/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            elif filial == "000014":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - lojaiguatemi/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            elif filial == "000015":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Iguatemi Alphaville/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            elif filial == "000016":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja JK Iguatemi/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            elif filial == "000012":
                with pd.ExcelWriter(f'{user_diretorio}/OneDrive - Austral/Documentos - Loja Morumbi/Mix diário/{self.excel_file_path}', engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)
            else:
                print('Filial desconhecida')
                with pd.ExcelWriter(self.excel_file_path, engine='openpyxl', mode='w') as writer:
                    df_combined.to_excel(writer, sheet_name='Mix Diário', index=False)

            messagebox.showinfo(
                "SUCESSO",
                f"ARQUIVO ATUALIZADO COM SUCESSO!\nARQUIVO: {self.excel_file_path}"
            )

            # Registra a última atualização
            self.last_update = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.update_last_update_label()

            # Limpa os dados após atualizar
            self.limpar_tudo()

        except Exception as e:
            messagebox.showerror(
                "ERRO",
                f"ERRO AO ATUALIZAR O ARQUIVO: {str(e)}"
            )

    def update_last_update_label(self):
        """Atualiza o label com a última ocorrência de atualização"""
        self.last_update_label.config(
            text=f"ÚLTIMA ATUALIZAÇÃO: {self.last_update}"
        )

        # Salva a última atualização nas configurações
        self.config.set('mix_diario.last_update', self.last_update)

    def save_progress(self):
        """Salva o progresso atual"""
        self.config.set('mix_diario.temp_data', {
            # Não salvar a loja selecionada
            'codigos': self.codigos
        })

        if hasattr(self, 'last_update'):
            self.config.set('mix_diario.last_update', self.last_update)

    def load_temp_data(self):
        """Carrega dados temporários sem selecionar a loja"""
        temp_data = self.config.get('mix_diario.temp_data', {})
        
        # Carrega códigos temporários
        for codigo in temp_data.get('codigos', []):
            self.tree.insert('', 'end', values=(
                codigo['data'],
                codigo['hora'],
                codigo['filial'],
                codigo['sku']
            ))
            self.codigos.append(codigo)

        self.last_update = self.config.get('mix_diario.last_update', 'NENHUMA')
        self.update_last_update_label()

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = MixDiarioApp(root)
    root.mainloop()