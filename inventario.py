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
        UIHelper.center_window(self.window, 1200, 600)
        
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
        
        # Frame de ações e status
        self.create_status_frame()
        self.create_action_frame()

    def create_location_frame(self):
        """Cria o frame de seleção de local"""
        location_frame = ttk.LabelFrame(
            self.main_frame,
            text="Local da Contagem",
            padding="10"
        )
        location_frame.pack(fill=tk.X, padx=5, pady=5)

        locations = [
            ('LOJA', 'loja'),
            ('ESTOQUE', 'estoque'),
            ('QUARTINHO ESCADA', 'quartinho_escada')
        ]

        for text, value in locations:
            ttk.Radiobutton(
                location_frame,
                text=text,
                value=value,
                variable=self.local_atual,
                style='primary'
            ).pack(side=tk.LEFT, padx=20)

    def create_input_frame(self):
        """Cria o frame de entrada de códigos"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=10)

        # Label código
        ttk.Label(
            input_frame,
            text="Código:",
            font=FONT_LABEL
        ).pack(side=tk.LEFT, padx=5)

        # Entry código
        self.entry_codigo = ttk.Entry(
            input_frame,
            textvariable=self.codigo,
            width=30,
            font=FONT_LABEL
        )
        self.entry_codigo.pack(side=tk.LEFT, padx=5)
        self.entry_codigo.bind('<Return>', self.registrar_codigo)

        # Botões
        ttk.Button(
            input_frame,
            text="REGISTRAR",
            command=self.registrar_codigo,
            style='primary.TButton',
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            input_frame,
            text="DESFAZER",
            command=self.desfazer_ultimo,
            style='danger.TButton',
            width=15
        ).pack(side=tk.LEFT, padx=5)

    def create_history_frame(self):
        """Cria o frame de histórico"""
        history_frame = ttk.LabelFrame(
            self.main_frame,
            text="Histórico de Leituras",
            padding="10"
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para o Treeview e Scrollbar
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Local', 'Código', 'Quantidade'),
            show='headings',
            height=15
        )

        # Configuração das colunas
        self.tree.heading('Local', text='Local', anchor=tk.W)
        self.tree.heading('Código', text='Código', anchor=tk.W)
        self.tree.heading('Quantidade', text='Quantidade', anchor=tk.E)

        # Configurar largura e alinhamento das colunas
        self.tree.column('Local', width=150, anchor=tk.W)
        self.tree.column('Código', width=200, anchor=tk.W)
        self.tree.column('Quantidade', width=100, anchor=tk.E)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar horizontal
        hsb = ttk.Scrollbar(history_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(fill=tk.X)
        self.tree.configure(xscrollcommand=hsb.set)

    def create_status_frame(self):
        """Cria o frame de status"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            font=('Helvetica', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

    def create_action_frame(self):
        """Cria o frame de ações finais"""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=10)

        # Botões de ação
        ttk.Button(
            action_frame,
            text="FINALIZAR INVENTÁRIO",
            command=self.finalizar_inventario,
            style='success.TButton',
            width=25
        ).pack(side=tk.RIGHT, padx=5)

        # Totais
        self.totais_var = tk.StringVar()
        ttk.Label(
            action_frame,
            textvariable=self.totais_var,
            font=FONT_LABEL
        ).pack(side=tk.LEFT, padx=5)

        self.atualizar_totais()

    def atualizar_totais(self):
        """Atualiza os totais mostrados na interface"""
        total_geral = sum(
            sum(local.values())
            for local in self.inventario.values()
        )
        self.totais_var.set(f"Total de itens: {total_geral}")

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
        self.atualizar_totais()
        self.status_var.set(
            f'Código {codigo} registrado no {local.upper()}. '
            f'Total: {self.inventario[local][codigo]}'
        )
        self.codigo.set('')
        self.entry_codigo.focus()

    @log_action("desfazer_codigo_inventario")
    def desfazer_ultimo(self):
        """Desfaz a última leitura"""
        if not self.historico_codigos:
            messagebox.showwarning(
                "Aviso",
                "Não há códigos para desfazer!"
            )
            return

        local, codigo = self.historico_codigos.pop()
        self.inventario[local][codigo] -= 1
        
        if self.inventario[local][codigo] == 0:
            del self.inventario[local][codigo]

        self.atualizar_historico()
        self.atualizar_totais()
        self.status_var.set(
            f'Última leitura desfeita: {codigo} do {local.upper()}'
        )

    def atualizar_historico(self):
        """Atualiza a visualização do histórico"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for local in self.inventario:
            for codigo, qtd in self.inventario[local].items():
                self.tree.insert(
                    '',
                    0,
                    values=(local.upper(), codigo, qtd)
                )

    @log_action("finalizar_inventario")
    def finalizar_inventario(self):
        """Finaliza o inventário e gera os arquivos"""
        if not any(self.inventario.values()):
            messagebox.showwarning(
                "Aviso",
                "Nenhum item registrado!"
            )
            return

        # Solicita diretório para salvar
        diretorio = filedialog.askdirectory(
            title="Selecione onde salvar os arquivos do inventário"
        )
        
        if not diretorio:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
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
                        writer.writerow([local.upper(), codigo, qtd])

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

            # Lista completa (agora em CSV)
            caminho_lista = os.path.join(
                diretorio,
                f'inventario_{timestamp}_lista_completa.csv'
            )
            with open(caminho_lista, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Código'])  # Cabeçalho
                for local in self.inventario:
                    for codigo, qtd in self.inventario[local].items():
                        # Repete o código conforme a quantidade
                        for _ in range(qtd):
                            writer.writerow([codigo])

            # Mostra resumo
            self.mostrar_resumo(
                caminho_detalhado,
                caminho_consolidado,
                caminho_lista
            )
            
        except Exception as e:
            self.logger.logger.error(f"Erro ao salvar arquivos: {str(e)}")
            messagebox.showerror(
                "Erro",
                "Ocorreu um erro ao salvar os arquivos do inventário!"
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