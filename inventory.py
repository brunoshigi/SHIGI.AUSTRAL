"""
Módulo de inventário para o sistema Austral.
Permite realizar contagem de estoque com separação por localização.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import csv
import os
from typing import Dict, List
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import ThemeManager, UIHelper, FONT_TITLE, FONT_LABEL

class InventoryApp:
    def __init__(self, window):
        self.window = window
        self.config = ConfigManager()
        self.logger = AustralLogger()
        
        # Configurações da janela
        self.window.title("INVENTÁRIO - CONTAGEM DE ESTOQUE")
        UIHelper.center_window(self.window, 800, 600)
        
        # Variáveis
        self.local_atual = tk.StringVar(value="loja")
        self.codigo = tk.StringVar()
        self.inventario = {
            'loja': {},
            'estoque': {},
            'quartinho_escada': {}
        }
        self.historico_codigos = []
        
        self.setup_ui()
        self.entry_codigo.focus()

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Container principal
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            self.main_frame,
            text="SISTEMA DE INVENTÁRIO",
            font=FONT_TITLE,
            justify="center"
        )
        title_label.pack(pady=(0, 20))

        # Frame de seleção de local
        self.create_location_frame()
        
        # Frame de entrada
        self.create_input_frame()
        
        # Frame de histórico
        self.create_history_frame()
        
        # Frame de ações
        self.create_action_frame()

    def create_location_frame(self):
        """Cria o frame de seleção de local"""
        location_frame = ttk.LabelFrame(
            self.main_frame,
            text="Local da Contagem",
            padding="10"
        )
        location_frame.pack(fill=tk.X, padx=5, pady=5)

        for local in ['loja', 'estoque', 'quartinho_escada']:
            ttk.Radiobutton(
                location_frame,
                text=local.upper(),
                value=local,
                variable=self.local_atual
            ).pack(side=tk.LEFT, padx=10)

    def create_input_frame(self):
        """Cria o frame de entrada de códigos"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Label(
            input_frame,
            text="Código:",
            font=FONT_LABEL
        ).pack(side=tk.LEFT, padx=5)

        self.entry_codigo = ttk.Entry(
            input_frame,
            textvariable=self.codigo,
            width=30
        )
        self.entry_codigo.pack(side=tk.LEFT, padx=5)
        self.entry_codigo.bind('<Return>', self.registrar_codigo)

        ttk.Button(
            input_frame,
            text="REGISTRAR",
            command=self.registrar_codigo,
            style='primary.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            input_frame,
            text="DESFAZER",
            command=self.desfazer_ultimo,
            style='danger.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def create_history_frame(self):
        """Cria o frame de histórico"""
        history_frame = ttk.LabelFrame(
            self.main_frame,
            text="Histórico de Leituras",
            padding="10"
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para histórico
        self.tree = ttk.Treeview(
            history_frame,
            columns=('Local', 'Código', 'Quantidade'),
            show='headings'
        )

        self.tree.heading('Local', text='Local')
        self.tree.heading('Código', text='Código')
        self.tree.heading('Quantidade', text='Quantidade')

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def create_action_frame(self):
        """Cria o frame de ações finais"""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)

        # Status bar
        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            action_frame,
            textvariable=self.status_var,
            font=('Helvetica', 10)
        )
        status_label.pack(side=tk.LEFT)

        ttk.Button(
            action_frame,
            text="FINALIZAR INVENTÁRIO",
            command=self.finalizar_inventario,
            style='success.TButton'
        ).pack(side=tk.RIGHT)

    @log_action("registrar_codigo_inventario")
    def registrar_codigo(self, event=None):
        """Registra um código no inventário"""
        codigo = self.codigo.get().strip()
        if not codigo:
            return
        
        local = self.local_atual.get()
        self.historico_codigos.append((local, codigo))
        
        if codigo in self.inventario[local]:
            self.inventario[local][codigo] += 1
        else:
            self.inventario[local][codigo] = 1

        self.atualizar_historico()
        self.status_var.set(f'Código {codigo} registrado no {local.upper()}. Total: {self.inventario[local][codigo]}')
        self.codigo.set('')
        self.entry_codigo.focus()

    @log_action("desfazer_codigo_inventario")
    def desfazer_ultimo(self):
        """Desfaz a última leitura"""
        if not self.historico_codigos:
            messagebox.showwarning("Aviso", "Não há códigos para desfazer!")
            return

        local, codigo = self.historico_codigos.pop()
        self.inventario[local][codigo] -= 1
        
        if self.inventario[local][codigo] == 0:
            del self.inventario[local][codigo]

        self.atualizar_historico()
        self.status_var.set(f'Última leitura desfeita: {codigo} do {local.upper()}')

    def atualizar_historico(self):
        """Atualiza a visualização do histórico"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for local in self.inventario:
            for codigo, qtd in self.inventario[local].items():
                self.tree.insert('', 0, values=(local, codigo, qtd))

    @log_action("finalizar_inventario")
    def finalizar_inventario(self):
        """Finaliza o inventário e gera os arquivos"""
        if not any(self.inventario.values()):
            messagebox.showwarning("Aviso", "Nenhum item registrado!")
            return

        # Solicita diretório para salvar
        diretorio = filedialog.askdirectory(
            title="Selecione onde salvar os arquivos do inventário"
        )
        
        if not diretorio:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Arquivo detalhado
        caminho_detalhado = os.path.join(
            diretorio,
            f'inventario_{timestamp}_detalhado.csv'
        )
        with open(caminho_detalhado, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Local', 'Código', 'Quantidade'])
            for local in self.inventario:
                for codigo, qtd in self.inventario[local].items():
                    writer.writerow([local, codigo, qtd])

        # Arquivo consolidado
        caminho_consolidado = os.path.join(
            diretorio,
            f'inventario_{timestamp}_consolidado.csv'
        )
        with open(caminho_consolidado, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Código', 'Quantidade Total'])
            
            codigos_totais = {}
            for local in self.inventario:
                for codigo, qtd in self.inventario[local].items():
                    codigos_totais[codigo] = codigos_totais.get(codigo, 0) + qtd
            
            for codigo, qtd in sorted(codigos_totais.items()):
                writer.writerow([codigo, qtd])

        # Lista completa
        caminho_lista = os.path.join(
            diretorio,
            f'inventario_{timestamp}_lista_completa.txt'
        )
        with open(caminho_lista, 'w', encoding='utf-8') as f:
            for local in self.inventario:
                for codigo, qtd in self.inventario[local].items():
                    for _ in range(qtd):
                        f.write(f'{codigo}\n')

        # Mostra resumo
        self.mostrar_resumo(
            caminho_detalhado,
            caminho_consolidado,
            caminho_lista
        )

    def mostrar_resumo(self, caminho_detalhado, caminho_consolidado, caminho_lista):
        """Mostra o resumo do inventário"""
        total_geral = 0
        resumo = "Resumo do Inventário:\n\n"
        
        for local in self.inventario:
            total_local = sum(self.inventario[local].values())
            qtd_itens = len(self.inventario[local])
            resumo += f"{local.upper()}:\n"
            resumo += f"Total de itens únicos: {qtd_itens}\n"
            resumo += f"Total de peças: {total_local}\n\n"
            total_geral += total_local
        
        resumo += f"TOTAL GERAL DE PEÇAS: {total_geral}\n\n"
        resumo += f"Arquivos salvos como:\n"
        resumo += f"- {caminho_detalhado}\n"
        resumo += f"- {caminho_consolidado}\n"
        resumo += f"- {caminho_lista}"

        messagebox.showinfo("Inventário Finalizado", resumo)
        self.window.destroy()