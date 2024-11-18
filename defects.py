# defect_manager_app.py

import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
from datetime import datetime
import sqlite3
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_TITLE, FONT_LABEL, FONT_ENTRY, FONT_BUTTON
from utils import UIHelper
from lojas import lojas

class DefectManagerApp:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.logger = AustralLogger()
        
        # Configuração inicial da janela
        self.root.title("SISTEMA AUSTRAL - REGISTRO DE DEFEITOS")
        
        # Reduzir o tamanho inicial da janela
        self.root.geometry("1200x600")
        
        # Configuração do banco de dados e interface
        self.setup_database()
        self.setup_ui()
        self.selected_item = None
        self.selected_id = None
        self.limpar_campos()
        
        # Centraliza a janela após ela ser criada
        self.center_window()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()  # Atualiza a geometria
        
        # Obtém as dimensões da tela e da janela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calcula a posição x,y para a janela
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Define a nova geometria
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def setup_database(self):
        """Configura a tabela de defeitos no banco de dados"""
        try:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defeitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_defeito TEXT,
                    codigo_produto TEXT,
                    descricao TEXT,
                    cor TEXT,
                    tamanho TEXT,
                    nome_cliente TEXT,
                    nome_vendedor TEXT,
                    data_defeito TEXT,
                    descricao_defeito TEXT,
                    observacoes TEXT,
                    loja TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
        except Exception as e:
            self.logger.logger.error(f"Erro ao configurar banco de dados: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                "Erro ao configurar banco de dados",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def setup_database_static(config):
        """Método estático para configurar o banco de dados sem instanciar a classe."""
        try:
            db_path = config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Criação da tabela 'defeitos'
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defeitos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_defeito TEXT,
                    codigo_produto TEXT,
                    descricao TEXT,
                    cor TEXT,
                    tamanho TEXT,
                    nome_cliente TEXT,
                    nome_vendedor TEXT,
                    data_defeito TEXT,
                    descricao_defeito TEXT,
                    observacoes TEXT,
                    loja TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        except Exception as e:
            # ... tratamento de erro existente ...
            pass
        finally:
            if 'conn' in locals():
                conn.close()

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Configuração do grid principal
        self.root.grid_rowconfigure(0, weight=1) # Expandir na vertical
        self.root.grid_columnconfigure(0, weight=1) # Expandir na horizontal
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding=20) # PADDING é um argumento de ttk.Frame 
        self.main_frame.grid(row=0, column=0, sticky='nsew') # NSEW = expandir em todas as direções
        
        # Título
        title_label = ttk.Label(
            self.main_frame,
            text="REGISTRO DE DEFEITOS",
            font=FONT_TITLE,
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))  # pady é um argumento de pack ou seja, o espaçamento entre o título e o próximo widget
        
        # Frame para campos de entrada
        entry_frame = ttk.Frame(self.main_frame) 
        entry_frame.pack(fill=tk.X, pady=(0, 10)) 
        
        # Frames da esquerda e direita
        left_frame = ttk.Frame(entry_frame)
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10) 
        
        right_frame = ttk.Frame(entry_frame)
        right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        # Configuração dos campos
        self.setup_entry_fields(left_frame, right_frame)
        
        # Frame de botões
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Configuração dos botões
        self.setup_buttons(button_frame)
        
        # Frame e configuração do Treeview
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_treeview(tree_frame)
        
        # Carregar dados iniciais
        self.carregar_dados()

    def setup_entry_fields(self, left_frame, right_frame):
        """Configura os campos de entrada"""
        # Listas de opções
        self.tipos_defeito = ["SELECIONE A ORIGEM", "CLIENTE", "LOJA", "UNIFORME"]
        self.tamanhos = ["SELECIONE O TAMANHO", "ÚNICO", "XPP", "PP", "P", "M", "G", "GG", "XGG",
                       "36", "38", "40", "42", "44", "46", "48",
                       "38-39", "40-41", "42-43", "44-45", "36-37", "34-35"]
        self.lojas_lista = ["SELECIONE A LOJA"]
        self.lojas_lista.extend([loja.get("loja", "") for loja in lojas if isinstance(loja, dict)])
        
        # Campos da esquerda
        self.create_field(left_frame, "ORIGEM DEFEITO **:", "tipo_defeito", self.tipos_defeito, 0)
        self.create_field(left_frame, "CÓDIGO PRODUTO **:", "codigo_produto", None, 1)
        self.create_field(left_frame, "NOME PRODUTO:", "descricao", None, 2)
        self.create_field(left_frame, "COR:", "cor", None, 3) # none 
        self.create_field(left_frame, "TAMANHO **:", "tamanho", self.tamanhos, 4)
        self.create_field(left_frame, "FILIAL:", "loja", self.lojas_lista, 5)
        
        # Campos da direita
        self.create_field(right_frame, "NOME CLIENTE:", "nome_cliente", None, 0)
        self.create_field(right_frame, "NOME VENDEDOR **:", "nome_vendedor", None, 1)
        self.create_field(right_frame, "DESCRIÇÃO DEFEITO **:", "descricao_defeito",
                         self.get_tipos_defeito(), 2)
        self.create_field(right_frame, "OBSERVAÇÕES:", "observacoes", None, 3,
                         is_text_area=True) # is_text_area é um argumento de create_field que define se o campo é uma área de texto 

    def create_field(self, parent, label_text, field_name, options=None, # 
                    row=0, is_text_area=False):
        """Cria um campo de entrada com label""" 
        ttk.Label(
            parent,
            text=label_text,
            font=FONT_LABEL
        ).grid(row=row, column=0, sticky='e', padx=5, pady=5) # sticky='e' alinha o texto à direita, padx=5 e pady=5 são espaçamentos
        
        if is_text_area:
            widget = ttk.Text(
                parent,
                height=3,
                width=35,
                font=FONT_ENTRY
            )
        elif options:
            widget = ttk.Combobox(
                parent,
                values=options,
                width=33 if field_name == "descricao_defeito" else 33,
                font=FONT_ENTRY,
                state='readonly'
            )
            widget.set(options[0])
        else:
            widget = ttk.Entry(
                parent,
                width=35 if field_name == "observacoes" else 35,
                font=FONT_ENTRY
            )
        
        widget.grid(row=row, column=1, sticky='w', padx=5, pady=5)
        setattr(self, f"{field_name}_entry", widget)

    def setup_buttons(self, button_frame):
        """Configura os botões da interface"""
        buttons = [
            ("ADICIONAR", self.adicionar_defeito, "primary"),
            ("ATUALIZAR", self.atualizar_defeito, "info"),
            ("EXCLUIR", self.excluir_defeito, "danger"),
            ("LIMPAR", self.limpar_campos, "warning"),
            ("EXPORTAR", self.exportar_excel, "success")
        ]
        
        for i, (text, command, style) in enumerate(buttons):
            button_frame.grid_columnconfigure(i, weight=1)
            btn = ttk.Button(
                button_frame,
                text=text,
                command=command,
                bootstyle=style,
                width=15
            )
            btn.grid(row=0, column=i, padx=2, sticky='nsew')  # Ajuste do padx e sticky
            # Expandir os botões para preencher o espaço disponível
            btn.grid(row=0, column=i, sticky='nsew', padx=2, pady=5)

    def setup_treeview(self, tree_frame):
        """Configura o Treeview"""
        # Configurar grid do frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Criar Treeview com colunas específicas
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "id",
                "tipo_defeito",
                "codigo_produto",
                "descricao",
                "nome_vendedor",
                "data_defeito",
                "cor",
                "tamanho",
                "loja",
                "observacoes"
            ),
            show="headings",
            height=10
        )
        
        # Configurar cabeçalhos e larguras das colunas
        colunas_config = {
            "id": ("ID", 40),
            "tipo_defeito": ("ORIGEM", 80),
            "codigo_produto": ("CÓDIGO", 90),
            "descricao": ("NOME PRODUTO", 200),
            "nome_vendedor": ("VENDEDOR", 125),
            "data_defeito": ("DATA", 90),
            "cor": ("COR", 100),
            "tamanho": ("TAM", 80),
            "loja": ("FILIAL", 170),
            "observacoes": ("OBSERVAÇÕES", 170)
        }
        
        for col, (heading, width) in colunas_config.items():
            self.tree.heading(col, text=heading, anchor='center')  # Centralizar cabeçalho
            self.tree.column(col, width=width, minwidth=width, anchor='center')  # Centralizar conteúdo
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Vincular eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)

    def on_double_click(self, event):
        """Manipula o duplo clique em um item da Treeview"""
        item = self.tree.selection()
        if not item:
            return
        
        # Obtém o item clicado
        item = item[0]
        # Obtém os valores do item
        valores = self.tree.item(item)['values']
        if not valores:
            return
        
        # Define o ID selecionado
        self.selected_id = valores[0]
        
        try:
            # Consulta o banco de dados
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM defeitos WHERE id = ?
            """, (self.selected_id,))
            
            row = cursor.fetchone()
            if row:
                # Limpa os campos atuais
                self.limpar_campos()
                
                # Preenche os campos com os dados do item selecionado
                self.tipo_defeito_entry.set(row[1])
                self.codigo_produto_entry.insert(0, row[2])
                self.descricao_entry.insert(0, row[3] or '')
                self.cor_entry.insert(0, row[4] or '')
                self.tamanho_entry.set(row[5])
                self.nome_cliente_entry.insert(0, row[6] or '')
                self.nome_vendedor_entry.insert(0, row[7])
                self.descricao_defeito_entry.set(row[9])
                self.observacoes_entry.insert('1.0', row[10] or '')
                self.loja_entry.set(row[11] if row[11] else self.lojas_lista[0])
                
        except Exception as e:
            self.logger.logger.error(f"Erro ao carregar dados do item: {str(e)}")
            UIHelper.show_message("ERRO", "Erro ao carregar dados do item selecionado", "error")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_tipos_defeito(self):
        """Retorna a lista expandida e organizada de tipos de defeito"""
        return [
        "SELECIONE UM TIPO DE DEFEITO",
        
        # Defeitos em Peças Novas
        "1. FUROS EM PEÇA NOVA",
        "2. MANCHA EM PEÇA NOVA",
        "3. FIO PUXADO EM PEÇA NOVA",
        "4. COSTURA TORTA",
        "5. COSTURA FROUXA",
        "6. COSTURA ROMPIDA",
        "7. ACABAMENTO IRREGULAR - SOBRAS DE LINHAS",
        "8. ACABAMENTO IRREGULAR - SOBRAS DE TECIDO",
        "9. ACABAMENTO IRREGULAR - PONTO SOLTO",
        "10. TECIDO TRANSPARENTE",
        "11. TECIDO COM FALHA DE TECELAGEM",
        "12. TECIDO COM FALHA DE TINGIMENTO",
        "13. TAMANHO INCORRETO",
        "14. ETIQUETA FALTANDO",
        "15. ETIQUETA COM INFORMAÇÃO INCORRETA",
        "16. ETIQUETA MAL POSICIONADA",
        "17. BOTÃO DIFERENTE DO PADRÃO",
        "18. BOTÃO MAL POSICIONADO",
        "19. ZÍPER QUEBRADO",
        "20. ZÍPER TRAVANDO",
        "21. BARRA SOLTA",
        "22. BARRA TORTA",
        "23. BARRA DESALINHADA",
        "24. PRODUTO TROCADO",
        "25. PRODUTO INCOMPLETO",
        
        # Defeitos em Aviamentos e Acabamentos
        "26. APLICAÇÃO SOLTANDO",
        "27. APLICAÇÃO MAL POSICIONADA",
        "28. APLICAÇÃO COM DEFEITO",
        "29. FALTA DE AVIAMENTOS",
        "30. AVIAMENTOS INCORRETOS",
        "31. AVIAMENTOS DANIFICADOS",
        "32. DEFEITO NA ESTAMPA - RACHADURA",
        "33. DEFEITO NA ESTAMPA - DESBOTAMENTO",
        "34. DEFEITO NA ESTAMPA - DESCASCAMENTO",
        "35. DEFEITO NA ESTAMPA - MANCHAS",
        "36. DEFEITO NO BORDADO - FALHAS",
        "37. DEFEITO NO BORDADO - PONTOS SOLTOS",
        "38. DEFEITO NO BORDADO - DESALINHAMENTO",
        "39. DEFEITO NO FORRO - COSTURA",
        "40. DEFEITO NO FORRO - MATERIAL",
        
        # Defeitos Após Uso e Lavagem
        "41. PILLING OU BOLINHAS",
        "42. PENUGEM APÓS LAVAGEM",
        "43. FURO APÓS USO",
        "44. FURO APÓS LAVAGEM",
        "45. MANCHA APÓS USO",
        "46. MANCHA APÓS LAVAGEM",
        "47. PEÇA DESCOSTURADA APÓS USO",
        "48. PEÇA DESCOSTURADA APÓS LAVAGEM",
        "49. DESBOTAMENTO APÓS USO",
        "50. DESBOTAMENTO APÓS LAVAGEM",
        "51. DESCOLORAÇÃO APÓS USO",
        "52. DESCOLORAÇÃO APÓS LAVAGEM",
        "53. MIGRAÇÃO DE COR",
        "54. BOTÃO CAINDO",
        "55. ENCOLHIMENTO APÓS LAVAGEM",
        "56. ENCOLHIMENTO IRREGULAR",
        "57. DEFORMAÇÃO APÓS LAVAGEM",
        
        # Defeitos por Condições Específicas
        "58. DEFEITO APÓS LAVAGEM E SECAGEM",
        "59. DEFEITO APÓS LAVAGEM E PASSAGEM",
        "60. DEFEITO APÓS ARMAZENAMENTO",
        "61. DEFEITO APÓS EXPOSIÇÃO AO SOL",
        "62. DEFEITO APÓS EXPOSIÇÃO À UMIDADE",
        "63. DESGASTE PRECOCE DO TECIDO",
        "64. DESGASTE IRREGULAR",
        "65. DESGASTE EM COSTURA",
        
        # Defeitos de Odor e Conservação
        "66. MAU CHEIRO PERSISTENTE",
        "67. MAU CHEIRO APÓS LAVAGEM",
        "68. MOFO",
        "69. MANCHAS DE UMIDADE",
        "70. AMARELAMENTO DO TECIDO",
        
        # Defeitos Estruturais
        "71. MODELAGEM INCORRETA",
        "72. PROPORÇÕES INCORRETAS",
        "73. CAIMENTO IRREGULAR",
        "74. ASSIMETRIA",
        "75. DEFEITO NA ESTRUTURA DO TECIDO",
        
        # Defeitos em Detalhes e Acessórios
        "76. DETALHE DESCOLADO",
        "77. DETALHE QUEBRADO",
        "78. DETALHE MAL POSICIONADO",
        "79. ACESSÓRIO DANIFICADO",
        "80. ACESSÓRIO FALTANTE",
        
        # Defeitos de Acabamento Especial
        "81. DEFEITO EM LAVANDERIA",
        "82. DEFEITO EM TINGIMENTO",
        "83. DEFEITO EM ESTAMPARIA",
        "84. DEFEITO EM BORDADO INDUSTRIAL",
        "85. DEFEITO EM TERMOCOLANTE",
        
        # Defeitos de Características Funcionais
        "86. PERDA DE ELASTICIDADE",
        "87. PERDA DE FORMA",
        "88. PERDA DE TEXTURA",
        "89. PERDA DE BRILHO",
        "90. FALHA NO ACABAMENTO ANTÍPILLING",
        
        # Outros Defeitos
        "91. FALHA NA COSTURA DECORATIVA",
        "92. FALHA NO ACABAMENTO IMPERMEÁVEL",
        "93. FALHA NO ACABAMENTO UV",
        "94. DEFEITO EM PEDRARIA",
        "95. DEFEITO EM APLICAÇÕES METÁLICAS"
    ]

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.tipo_defeito_entry.set(self.tipos_defeito[0])
        self.codigo_produto_entry.delete(0, tk.END)
        self.descricao_entry.delete(0, tk.END)
        self.cor_entry.delete(0, tk.END)
        self.tamanho_entry.set(self.tamanhos[0])
        self.loja_entry.set(self.lojas_lista[0])
        self.nome_cliente_entry.delete(0, tk.END)
        self.nome_vendedor_entry.delete(0, tk.END)
        self.descricao_defeito_entry.set(self.get_tipos_defeito()[0])
        self.observacoes_entry.delete('1.0', tk.END) 
        
        
        # self.selected_item = None
        # self.selected_id = None

    def on_select(self, event):
        """Manipula a seleção de um item na Treeview"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        self.selected_item = selected_items[0]
        valores = self.tree.item(self.selected_item)['values']
        if not valores:
            return

        self.selected_id = valores[0]  # ID do defeito

        try:
            # Consulta o banco de dados para obter os dados completos
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM defeitos WHERE id = ?
            """, (self.selected_id,))

            row = cursor.fetchone()
            if row:
                # Limpa os campos atuais sem redefinir a seleção
                self.tipo_defeito_entry.set(self.tipos_defeito[0])
                self.codigo_produto_entry.delete(0, tk.END)
                self.descricao_entry.delete(0, tk.END)
                self.cor_entry.delete(0, tk.END)
                self.tamanho_entry.set(self.tamanhos[0])
                self.loja_entry.set(self.lojas_lista[0])
                self.nome_cliente_entry.delete(0, tk.END)
                self.nome_vendedor_entry.delete(0, tk.END)
                self.descricao_defeito_entry.set(self.get_tipos_defeito()[0])
                self.observacoes_entry.delete('1.0', tk.END)

                # Preenche os campos com os dados do item selecionado
                self.tipo_defeito_entry.set(row[1])
                self.codigo_produto_entry.insert(0, row[2])
                self.descricao_entry.insert(0, row[3] or '')
                self.cor_entry.insert(0, row[4] or '')
                self.tamanho_entry.set(row[5])
                self.nome_cliente_entry.insert(0, row[6] or '')
                self.nome_vendedor_entry.insert(0, row[7])
                self.descricao_defeito_entry.set(row[9])
                self.observacoes_entry.insert('1.0', row[10] or '')
                self.loja_entry.set(row[11] if row[11] else self.lojas_lista[0])

        except Exception as e:
            self.logger.logger.error(f"Erro ao carregar dados do item: {str(e)}")
            UIHelper.show_message("ERRO", "Erro ao carregar dados do item selecionado", "error")
        finally:
            if 'conn' in locals():
                conn.close()

    def carregar_dados(self):
        """Carrega os dados do banco de dados para a Treeview"""
        # Limpar dados existentes
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tipo_defeito, codigo_produto, descricao,
                       nome_vendedor, data_defeito, cor, tamanho,
                       loja, observacoes
                FROM defeitos
                ORDER BY id DESC
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                self.tree.insert("", "end", values=row)
                
        except Exception as e:
            self.logger.logger.error(f"Erro ao carregar dados: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                "Erro ao carregar dados da tabela",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def adicionar_defeito(self):
        """Adiciona um novo defeito ao banco de dados"""
        # Validar campos obrigatórios
        if not self._validar_campos_obrigatorios():
            return

        try:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO defeitos (
                    tipo_defeito, codigo_produto, descricao, cor, tamanho,
                    nome_cliente, nome_vendedor, data_defeito,
                    descricao_defeito, observacoes, loja
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.tipo_defeito_entry.get(),
                self.codigo_produto_entry.get(),
                self.descricao_entry.get(),
                self.cor_entry.get(),
                self.tamanho_entry.get(),
                self.nome_cliente_entry.get(),
                self.nome_vendedor_entry.get(),
                datetime.now().strftime('%Y-%m-%d'),
                self.descricao_defeito_entry.get(),
                self.observacoes_entry.get('1.0', tk.END).strip(),
                self.loja_entry.get()
            ))
            
            conn.commit()
            
            # Registrar ação no log
            self.logger.log_action(
                "defeito_adicionado",
                f"Código: {self.codigo_produto_entry.get()}"
            )
            
            self.carregar_dados()
            self.limpar_campos()
            
            UIHelper.show_message(
                "Sucesso",
                "Defeito registrado com sucesso!",
                "info"
            )
            
        except Exception as e:
            self.logger.logger.error(f"Erro ao adicionar defeito: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                "Erro ao adicionar defeito",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def atualizar_defeito(self):
        """Atualiza um defeito existente"""
        if not self.selected_id:
            UIHelper.show_message(
                "Aviso",
                "Por favor, selecione um defeito para atualizar",
                "warning"
            )
            return

        if not self._validar_campos_obrigatorios():
            return

        try:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE defeitos SET
                    tipo_defeito = ?,
                    codigo_produto = ?,
                    descricao = ?,
                    cor = ?,
                    tamanho = ?,
                    nome_cliente = ?,
                    nome_vendedor = ?,
                    descricao_defeito = ?,
                    observacoes = ?,
                    loja = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                self.tipo_defeito_entry.get(),
                self.codigo_produto_entry.get(),
                self.descricao_entry.get(),
                self.cor_entry.get(),
                self.tamanho_entry.get(),
                self.nome_cliente_entry.get(),
                self.nome_vendedor_entry.get(),
                self.descricao_defeito_entry.get(),
                self.observacoes_entry.get('1.0', tk.END).strip(),
                self.loja_entry.get(),
                self.selected_id
            ))
            
            conn.commit()
            
            self.logger.log_action(
                "defeito_atualizado",
                f"ID: {self.selected_id}"
            )
            
            self.carregar_dados()
            self.limpar_campos()
            
            UIHelper.show_message(
                "Sucesso",
                "Defeito atualizado com sucesso!",
                "info"
            )
            
        except Exception as e:
            self.logger.logger.error(f"Erro ao atualizar defeito: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                "Erro ao atualizar defeito",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def excluir_defeito(self):
        """Exclui um defeito do banco de dados"""
        if not self.selected_id:
            UIHelper.show_message(
                "Aviso",
                "Por favor, selecione um defeito para excluir",
                "warning"
            )
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Tem certeza que deseja excluir este registro?"
        ):
            return

        try:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM defeitos WHERE id = ?', (self.selected_id,))
            conn.commit()

            self.logger.log_action(
                "defeito_excluido",
                f"ID: {self.selected_id}"
            )

            self.carregar_dados()
            self.limpar_campos()

            UIHelper.show_message(
                "Sucesso",
                "Defeito excluído com sucesso!",
                "info"
            )

        except Exception as e:
            self.logger.logger.error(f"Erro ao excluir defeito: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                "Erro ao excluir defeito",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def exportar_excel(self):
        """Exporta os dados para um arquivo Excel"""
        try:
            # Diálogo para escolher o local de salvamento
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Salvar Arquivo Excel",
                initialfile=f"defeitos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not file_path:
                return

            # Carregar dados do banco
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            
            query = """
                SELECT 
                    tipo_defeito as 'TIPO DE DEFEITO',
                    codigo_produto as 'CÓDIGO DO PRODUTO',
                    descricao as 'DESCRIÇÃO',
                    cor as 'COR',
                    tamanho as 'TAMANHO',
                    nome_cliente as 'NOME DO CLIENTE',
                    nome_vendedor as 'NOME DO VENDEDOR',
                    data_defeito as 'DATA DO DEFEITO',
                    descricao_defeito as 'DESCRIÇÃO DO DEFEITO',
                    observacoes as 'OBSERVAÇÕES',
                    loja as 'LOJA',
                    created_at as 'DATA DE CRIAÇÃO',
                    updated_at as 'ÚLTIMA ATUALIZAÇÃO'
                FROM defeitos
                ORDER BY id DESC
            """
            
            df = pd.read_sql_query(query, conn)

            # Configurar o writer do Excel
            writer = pd.ExcelWriter(file_path, engine='openpyxl')

            # Exportar para Excel com formatação
            df.to_excel(writer, index=False, sheet_name='DEFEITOS')

            # Ajustar larguras das colunas
            worksheet = writer.sheets['DEFEITOS']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col))
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

            writer.close()
            
            self.logger.log_action(
                "dados_exportados",
                f"Arquivo: {file_path}"
            )
            
            UIHelper.show_message(
                "Sucesso",
                f"Dados exportados com sucesso para:\n{file_path}",
                "info"
            )
            
        except Exception as e:
            self.logger.logger.error(f"Erro ao exportar dados: {str(e)}")
            UIHelper.show_message(
                "ERRO",
                f"Erro ao exportar dados:\n{str(e)}",
                "error"
            )
        finally:
            if 'conn' in locals():
                conn.close()

    def _validar_campos_obrigatorios(self):
        """Valida os campos obrigatórios do formulário"""
        campos_obrigatorios = {
            'ORIGEM DEFEITO': self.tipo_defeito_entry.get(),
            'CÓDIGO PRODUTO': self.codigo_produto_entry.get(),
            'TAMANHO': self.tamanho_entry.get(),
            'NOME DO VENDEDOR': self.nome_vendedor_entry.get(),
            'DESCRIÇÃO DEFEITO': self.descricao_defeito_entry.get()
        }

        # Opções inválidas que devem ser ignoradas
        opcoes_invalidas = [
            "SELECIONE A ORIGEM", "SELECIONE O TAMANHO", "SELECIONE A LOJA", 
            "SELECIONE UM TIPO DE DEFEITO"
        ]

        # Filtra os campos que estão vazios ou têm opções inválidas
        campos_vazios = [
            campo for campo, valor in campos_obrigatorios.items()
            if not valor or valor in opcoes_invalidas
        ]

        if campos_vazios:
            UIHelper.show_message(
                "Aviso",
                f"Os seguintes campos são obrigatórios:\n{', '.join(campos_vazios)}",
                "warning"
            )
            return False

        return True

# Verificação do ambiente principal
if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = DefectManagerApp(root)
    root.mainloop()
