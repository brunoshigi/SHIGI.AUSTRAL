import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import ttkbootstrap as ttk
import sqlite3
import pandas as pd
from datetime import datetime
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_LABEL, FONT_ENTRY
from utils import setup_window_icon
from utils import UIHelper

class PedidoSinOMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA AUSTRAL - CONTROLE DE ENVIO DE PEDIDOS SINOMS")
        self.config = ConfigManager()
        self.logger = AustralLogger()

        self.setup_database()
        setup_window_icon(self.root)
        self.setup_ui()
        self.carregar_dados()
        self.center_window()

    def center_window(self):
        """Centraliza a janela principal no ecrã."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_database(self):
        db_path = self.config.get('database.path', 'austral.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_faturamento TEXT,
                responsavel_faturamento TEXT,
                numero_pedido TEXT UNIQUE,
                status TEXT DEFAULT 'Faturado',
                data_envio TEXT,
                responsavel_envio TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        # Configuração da grade da janela principal
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Área de entrada de dados (Topo)
        entry_frame = ttk.Frame(self.root, padding="10")
        entry_frame.grid(row=0, column=0, sticky='ew')

        # Configurar colunas do frame de entrada
        entry_frame.grid_columnconfigure(0, weight=1)
        entry_frame.grid_columnconfigure(1, weight=1)
        entry_frame.grid_columnconfigure(2, weight=1)

        # Labels e Entradas de Dados (em maiúsculas)
        ttk.Label(entry_frame, text="RESPONSÁVEL:", font=FONT_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.responsavel_entry = ttk.Entry(entry_frame, font=FONT_ENTRY)
        self.responsavel_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(entry_frame, text="NÚMERO DO PEDIDO:", font=FONT_LABEL).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.numero_pedido_entry = ttk.Entry(entry_frame, font=FONT_ENTRY)
        self.numero_pedido_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Botão Registrar Pedido (Centralizado)
        add_button = ttk.Button(entry_frame, text="REGISTRAR PEDIDO", command=self.adicionar_pedido, style="primary.TButton")
        add_button.grid(row=1, column=0, columnspan=4, pady=10)

        # Tabela
        self.tree = ttk.Treeview(self.root, columns=("DATA", "RESPONSÁVEL", "PEDIDO", "STATUS", "ENVIO", "RESPONSÁVEL ENVIO"), show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

        # Configurar largura e centralização das colunas
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center", width=120)
            self.tree.heading(col, text=col, anchor="center")

        # Frame de Ações (Rodapé)
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.grid(row=2, column=0, sticky='ew')

        # Configuração de colunas para centralizar os botões de ação
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Botões de Ação em Maiúsculas
        ttk.Button(action_frame, text="MARCAR COMO ENVIADO", command=self.marcar_como_enviado, style="Warning.TButton").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(action_frame, text="EXCLUIR PEDIDO", command=self.excluir_pedido, style="danger.TButton").grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(action_frame, text="EXPORTAR PARA EXCEL", command=self.exportar_excel, style="success.TButton").grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    @log_action("add_order")
    def adicionar_pedido(self):
        """Adiciona um novo pedido usando a data atual no formato brasileiro"""
        data_faturamento = datetime.now().strftime('%d/%m/%Y')
        responsavel = self.responsavel_entry.get().upper()  # Converter para maiúsculas
        numero_pedido = self.numero_pedido_entry.get().upper()  # Converter para maiúsculas

        if not responsavel or not numero_pedido:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        db_path = self.config.get('database.path', 'austral.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pedidos (data_faturamento, responsavel_faturamento, numero_pedido)
                VALUES (?, ?, ?)
            ''', (data_faturamento, responsavel, numero_pedido))
            conn.commit()
            self.carregar_dados()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Erro", "Número de pedido já existe.")
        finally:
            conn.close()

    @log_action("load_orders")
    def carregar_dados(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        db_path = self.config.get('database.path', 'austral.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT data_faturamento, responsavel_faturamento, numero_pedido, status, data_envio, responsavel_envio FROM pedidos')
        
        for row in cursor.fetchall():
            valores = list(row)
            if valores[0]:  # data_faturamento
                try:
                    data = datetime.strptime(valores[0], '%Y-%m-%d').strftime('%d/%m/%Y')
                    valores[0] = data
                except ValueError:
                    pass
            
            if valores[4]:  # data_envio
                try:
                    data = datetime.strptime(valores[4], '%Y-%m-%d').strftime('%d/%m/%Y')
                    valores[4] = data
                except ValueError:
                    pass
                
            self.tree.insert("", "end", values=[str(v).upper() for v in valores])  # Converter tudo para maiúsculas
        conn.close()

    @log_action("mark_as_sent")
    def marcar_como_enviado(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um pedido.")
            return

        pedido = self.tree.item(selected_item)["values"][2]
        responsavel_envio = simpledialog.askstring("Responsável pelo Envio", "Digite o nome do responsável pelo envio:")

        if responsavel_envio:
            data_envio = datetime.now().strftime("%d/%m/%Y")
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE pedidos SET status="Enviado", data_envio=?, responsavel_envio=? WHERE numero_pedido=?
            ''', (data_envio, responsavel_envio.upper(), pedido))
            conn.commit()
            conn.close()
            self.carregar_dados()

    @log_action("delete_order")
    def excluir_pedido(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um pedido para excluir.")
            return

        pedido = self.tree.item(selected_item)["values"][2]
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o pedido {pedido}?"):
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM pedidos WHERE numero_pedido=?', (pedido,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Pedido excluído com sucesso!")
                self.carregar_dados()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir pedido: {str(e)}")
            finally:
                conn.close()

    @log_action("export_to_excel")
    def exportar_excel(self):
        data_atual = datetime.now().strftime("%d%m%Y")
        nome_arquivo = f"sinoms_{data_atual}.xlsx"
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=nome_arquivo,
            title="Salvar arquivo Excel",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if export_path:
            db_path = self.config.get('database.path', 'austral.db')
            conn = sqlite3.connect(db_path)
            try:
                df = pd.read_sql_query('SELECT * FROM pedidos', conn)
                df.columns = [col.upper() for col in df.columns]  # Converter cabeçalhos para maiúsculas
                df.to_excel(export_path, index=False)
                messagebox.showinfo("Sucesso", f"Dados exportados para {export_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
            finally:
                conn.close()

# Verificação do ambiente principal
if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = PedidoSinOMSApp(root)
    root.mainloop()
