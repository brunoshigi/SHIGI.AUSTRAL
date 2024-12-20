import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from tkinter import messagebox
import pandas as pd
from utils import UIHelper, setup_window_icon
from logger import AustralLogger, log_action
from config import ConfigManager
from pathlib import Path

class PontoDeVendaApp:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.logger = AustralLogger()

        self.root.title("SIMULADOR DE VENDAS - AUSTRAL")
        setup_window_icon(self.root)
        
        self.root.minsize(1100, 600)
        UIHelper.center_window(self.root, width=1100, height=600)

        self.total = 0.0
        self.produtos = []
        self.produto_precos = {}
        self.produto_descricoes = {}

        self.carregar_dados()
        self.setup_ui()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        self.root.bind('<F2>', lambda e: self.limpar_tudo())
        self.root.bind('<F5>', lambda e: self.finalizar_venda())
        self.root.bind('<Delete>', lambda e: self.remover_produto())
        self.codigo_entry.bind("<Return>", self.adicionar_produto)

    def carregar_dados(self):
        try:
            file_path = r"C:\Users\geren\Downloads\data.xlsx"
            df = pd.read_excel(file_path)
            self.produto_precos = {
                str(codigo).lower(): preco for codigo, preco in zip(df['codigo_barras'], df['preco_produto'])
            }
            self.produto_descricoes = {
                str(codigo).lower(): desc for codigo, desc in zip(df['codigo_barras'], df['desc_produto'])
            }
        except Exception as e:
            self.logger.logger.error(f"Erro ao carregar dados: {str(e)}")
            messagebox.showerror("ERRO", f"ERRO AO CARREGAR OS DADOS: {str(e)}")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=ttk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=ttk.X, pady=(0, 15))

        titulo_frame = ttk.Frame(header_frame)
        titulo_frame.pack(side=ttk.LEFT)
        
        logo_label = ttk.Label(titulo_frame, text="AUSTRAL", 
                               font=("Helvetica", 12, "bold"), 
                               bootstyle="primary")
        logo_label.pack()
        
        ttk.Label(titulo_frame, 
                  text="SIMULADOR DE VENDAS", 
                  font=("Helvetica", 24, "bold"), 
                  bootstyle="primary").pack()

        header_right = ttk.Frame(header_frame)
        header_right.pack(side=ttk.RIGHT)

        self.time_label = ttk.Label(header_right, 
                                    text="", 
                                    font=("Helvetica", 12))
        self.time_label.pack(side=ttk.BOTTOM)
        self.update_time()

        input_frame = ttk.LabelFrame(main_frame, 
                                     text="ENTRADA DE PRODUTOS", 
                                     padding="15",
                                     bootstyle="primary")
        input_frame.pack(fill=ttk.X, pady=(0, 15))

        ttk.Label(input_frame, 
                  text="CÓDIGO:", 
                  font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
        
        self.codigo_entry = ttk.Entry(input_frame, 
                                      font=("Helvetica", 12), 
                                      width=30)
        self.codigo_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, 
                  text="QUANTIDADE:", 
                  font=("Helvetica", 12)).grid(row=0, column=2, padx=5)
        
        self.quantidade_entry = ttk.Entry(input_frame, 
                                          font=("Helvetica", 12), 
                                          width=5)
        self.quantidade_entry.grid(row=0, column=3, padx=5)
        self.quantidade_entry.insert(0, "1")

        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=0, column=4, padx=15)

        ttk.Button(buttons_frame, 
                   text="ADICIONAR (ENTER)", 
                   command=self.adicionar_produto, 
                   bootstyle="primary").pack(side=ttk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, 
                   text="REMOVER (DEL)", 
                   command=self.remover_produto, 
                   bootstyle="danger").pack(side=ttk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(main_frame, 
                                    text="PRODUTOS", 
                                    padding="15",
                                    bootstyle="primary")
        list_frame.pack(fill=ttk.BOTH, expand=True, pady=(0, 15))

        self.tree = ttk.Treeview(
            list_frame,
            columns=("codigo", "descricao", "quantidade", "preco", "subtotal"),
            show="headings",
            height=15
        )

        self.tree.heading("codigo", text="CÓDIGO")
        self.tree.heading("descricao", text="DESCRIÇÃO")
        self.tree.heading("quantidade", text="QTD")
        self.tree.heading("preco", text="PREÇO UNIT.")
        self.tree.heading("subtotal", text="SUBTOTAL")

        self.tree.column("codigo", width=100, anchor="center")
        self.tree.column("descricao", width=350, anchor="w")
        self.tree.column("quantidade", width=70, anchor="center")
        self.tree.column("preco", width=100, anchor="center")
        self.tree.column("subtotal", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)
        scrollbar.pack(side=ttk.RIGHT, fill=ttk.Y)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=ttk.X)

        left_buttons = ttk.Frame(bottom_frame)
        left_buttons.pack(side=ttk.LEFT)

        ttk.Button(left_buttons, 
                   text="NOVA VENDA (F2)", 
                   command=self.limpar_tudo, 
                   bootstyle="warning").pack(side=ttk.LEFT, padx=5)

        right_frame = ttk.Frame(bottom_frame)
        right_frame.pack(side=ttk.RIGHT)

        self.total_label = ttk.Label(right_frame, 
                                     text="TOTAL: R$ 0,00", 
                                     font=("Helvetica", 18, "bold"), 
                                     bootstyle="primary")
        self.total_label.pack(side=ttk.LEFT, padx=15)

        ttk.Button(right_frame, 
                   text="FINALIZAR VENDA (F5)", 
                   command=self.finalizar_venda, 
                   bootstyle="success").pack(side=ttk.LEFT)

    def update_time(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    @log_action("add_product")
    def adicionar_produto(self, event=None):
        codigo = self.codigo_entry.get().strip().lower()
        quantidade = self.quantidade_entry.get().strip()
        
        if not codigo:
            messagebox.showwarning("ATENÇÃO", "DIGITE UM CÓDIGO DE BARRAS!")
            return
            
        if not quantidade.isdigit() or int(quantidade) <= 0:
            messagebox.showerror("ERRO", "QUANTIDADE INVÁLIDA!")
            return

        quantidade = int(quantidade)
        if codigo in self.produto_precos:
            preco = self.produto_precos[codigo]
            descricao = self.produto_descricoes.get(codigo, "DESCRIÇÃO NÃO DISPONÍVEL")
            subtotal = quantidade * preco
            self.produtos.append((codigo, descricao, quantidade, preco, subtotal))

            self.tree.insert("", "end", values=(
                codigo,
                descricao,
                quantidade,
                f"R$ {preco:.2f}",
                f"R$ {subtotal:.2f}"
            ))

            self.total += subtotal
            self.total_label.config(text=f"TOTAL: R$ {self.total:.2f}")

            self.codigo_entry.delete(0, "end")
            self.quantidade_entry.delete(0, "end")
            self.quantidade_entry.insert(0, "1")
            self.codigo_entry.focus()
        else:
            messagebox.showerror("ERRO", "PRODUTO NÃO ENCONTRADO!")

    def remover_produto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("ATENÇÃO", "SELECIONE UM PRODUTO PARA REMOVER!")
            return

        item = self.tree.item(selected_item[0])
        valores = item['values']
        subtotal_str = valores[4].replace('R$ ', '').replace(',', '.')
        subtotal = float(subtotal_str)

        self.total -= subtotal
        self.total_label.config(text=f"TOTAL: R$ {self.total:.2f}")

        self.produtos = [p for p in self.produtos if not (p[0] == valores[0] and p[1] == valores[1])]
        self.tree.delete(selected_item[0])

    def limpar_tudo(self):
        if self.produtos:
            if not messagebox.askyesno("CONFIRMAÇÃO", "DESEJA REALMENTE LIMPAR TODOS OS PRODUTOS?"):
                return

        self.produtos.clear()
        self.tree.delete(*self.tree.get_children())
        self.total = 0.0
        self.total_label.config(text="TOTAL: R$ 0,00")
        self.codigo_entry.focus()

    def finalizar_venda(self):
        if not self.produtos:
            messagebox.showwarning("ATENÇÃO", "NENHUM PRODUTO NA LISTA!")
            return

        recibo = "=== AUSTRAL ===\n"
        recibo += f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        recibo += "=" * 40 + "\n\n"
        
        for codigo, desc, qtd, preco, subtotal in self.produtos:
            recibo += f"{desc}\n"
            recibo += f"{qtd}x R$ {preco:.2f} = R$ {subtotal:.2f}\n\n"
        
        recibo += "=" * 40 + "\n"
        recibo += f"TOTAL: R$ {self.total:.2f}\n"
        recibo += "=" * 40 + "\n"
        recibo += "\nOBRIGADO PELA PREFERÊNCIA!"

        messagebox.showinfo("VENDA FINALIZADA", recibo)
        self.limpar_tudo()


if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = PontoDeVendaApp(root)
    root.mainloop()
