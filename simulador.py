import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from tkinter import messagebox, simpledialog
import tkinter as tk
import pandas as pd
from utils import UIHelper, setup_window_icon
from logger import AustralLogger, log_action
from config import ConfigManager
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile
from pathlib import Path
import sys

def get_resource_path(filename: str) -> str:
    """Retorna o caminho correto para um recurso na raiz do projeto"""
    try:
        if getattr(sys, '_MEIPASS', False):
            return os.path.join(sys._MEIPASS, filename)
        
        base_path = Path(__file__).resolve().parent
        resource_path = base_path / filename

        if resource_path.exists():
            return str(resource_path)
        raise FileNotFoundError(f"Recurso não encontrado: {filename}")
    except Exception as e:
        print(f"Erro ao localizar recurso {filename}: {e}")
        return None

class PontoDeVendaApp:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.logger = AustralLogger()

        self.root.title("SIMULADOR DE VENDAS - AUSTRAL")
        setup_window_icon(self.root)

        self.root.minsize(900, 500)  # Reduzido o tamanho mínimo
        UIHelper.center_window(self.root, width=900, height=500)

        self.total = 0.0
        self.produtos = []
        self.produto_precos = {}
        self.produto_descricoes = {}
        self.trocas = 0.0

        self.LARGURA_PAPEL = 500
        self.ALTURA_ETIQUETA = 700
        self.MARGEM = 20

        self.carregar_dados()
        self.setup_ui()
        self.setup_shortcuts()
        self.ticket_number = None

    def setup_shortcuts(self):
        self.root.bind('<F2>', lambda e: self.limpar_tudo())
        self.root.bind('<F5>', lambda e: self.finalizar_venda())
        self.root.bind('<Delete>', lambda e: self.remover_produto())
        self.root.bind('<F7>', lambda e: self.adicionar_troca())
        self.codigo_entry.bind("<Return>", self.adicionar_produto)

    def carregar_dados(self):
        try:
            file_path = r"C:\\Users\\geren\\Downloads\\data.xlsx"
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
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=ttk.BOTH, expand=True)

        self.setup_header(main_frame)
        self.setup_input_frame(main_frame)
        self.setup_list_frame(main_frame)
        self.setup_bottom_frame(main_frame)

    def setup_header(self, main_frame):
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=ttk.X, pady=(0, 10))

        titulo_frame = ttk.Frame(header_frame)
        titulo_frame.pack(side=ttk.LEFT)

        ttk.Label(titulo_frame, text="AUSTRAL", 
                 font=("Helvetica", 10, "bold"),
                 bootstyle="primary").pack()

        ttk.Label(titulo_frame, 
                 text="SIMULADOR DE VENDAS", 
                 font=("Helvetica", 18, "bold"),
                 bootstyle="primary").pack()

        header_right = ttk.Frame(header_frame)
        header_right.pack(side=ttk.RIGHT)

        self.time_label = ttk.Label(header_right, 
                                  text="", 
                                  font=("Helvetica", 10))
        self.time_label.pack(side=ttk.BOTTOM)

    def setup_input_frame(self, main_frame):
        input_frame = ttk.LabelFrame(main_frame, 
                                   text="ENTRADA DE PRODUTOS", 
                                   padding="5",
                                   bootstyle="primary")
        input_frame.pack(fill=ttk.X, pady=(0, 10))

        # Frame superior para código, quantidade e tipo
        top_frame = ttk.Frame(input_frame)
        top_frame.pack(fill=ttk.X, padx=5, pady=2)

        # Frame para código
        codigo_frame = ttk.Frame(top_frame)
        codigo_frame.pack(side=ttk.LEFT, padx=2)
        ttk.Label(codigo_frame, text="CÓDIGO:", font=("Helvetica", 10)).pack(side=ttk.LEFT, padx=2)
        self.codigo_entry = ttk.Entry(codigo_frame, font=("Helvetica", 10), width=30)
        self.codigo_entry.pack(side=ttk.LEFT)

        # Frame para quantidade
        qtd_frame = ttk.Frame(top_frame)
        qtd_frame.pack(side=ttk.LEFT, padx=2)
        ttk.Label(qtd_frame, text="QTD:", font=("Helvetica", 10)).pack(side=ttk.LEFT, padx=2)
        self.quantidade_entry = ttk.Entry(qtd_frame, font=("Helvetica", 10), width=5)
        self.quantidade_entry.pack(side=ttk.LEFT)
        self.quantidade_entry.insert(0, "1")

        # Frame para tipo
        tipo_frame = ttk.Frame(top_frame)
        tipo_frame.pack(side=ttk.LEFT, padx=2)
        ttk.Label(tipo_frame, text="TIPO:", font=("Helvetica", 10)).pack(side=ttk.LEFT, padx=2)
        self.tipo_operacao = ttk.Combobox(tipo_frame,
                                        values=["VENDA", "TROCA"],
                                        font=("Helvetica", 10),
                                        width=8,
                                        state="readonly")
        self.tipo_operacao.pack(side=ttk.LEFT)
        self.tipo_operacao.set("VENDA")

        # Frame para botões
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=ttk.LEFT, padx=2)
        ttk.Button(buttons_frame, 
                  text="ADICIONAR (ENT)", 
                  command=self.adicionar_produto, 
                  bootstyle="primary",
                  width=20).pack(side=ttk.LEFT, padx=2)
        ttk.Button(buttons_frame, 
                  text="REMOVER (DEL)", 
                  command=self.remover_produto, 
                  bootstyle="danger",
                  width=15).pack(side=ttk.LEFT, padx=2)

        # Frame inferior para número do ticket
        bottom_frame = ttk.Frame(input_frame)
        bottom_frame.pack(fill=ttk.X, padx=5, pady=2)
        ttk.Label(bottom_frame,
                text="TICKET:",
                font=("Helvetica", 10)).pack(side=ttk.LEFT, padx=2)
        self.ticket_entry = ttk.Entry(bottom_frame,
                                   font=("Helvetica", 10),
                                   width=12)
        self.ticket_entry.pack(side=ttk.LEFT, padx=2)

    def setup_list_frame(self, main_frame):
        list_frame = ttk.LabelFrame(main_frame, 
                                  text="PRODUTOS", 
                                  padding="5",
                                  bootstyle="primary")
        list_frame.pack(fill=ttk.BOTH, expand=True, pady=(0, 10))

        self.tree = ttk.Treeview(
            list_frame,
            columns=("codigo", "descricao", "quantidade", "preco", "subtotal", "tipo"),
            show="headings",
            height=12
        )

        self.tree.heading("codigo", text="CÓDIGO")
        self.tree.heading("descricao", text="DESCRIÇÃO")
        self.tree.heading("quantidade", text="QTD")
        self.tree.heading("preco", text="PREÇO UNIT.")
        self.tree.heading("subtotal", text="SUBTOTAL")
        self.tree.heading("tipo", text="TIPO")

        self.tree.column("codigo", width=80, anchor="center")
        self.tree.column("descricao", width=250, anchor="w")
        self.tree.column("quantidade", width=50, anchor="center")
        self.tree.column("preco", width=80, anchor="center")
        self.tree.column("subtotal", width=80, anchor="center")
        self.tree.column("tipo", width=60, anchor="center")

        self.tree.tag_configure('troca', foreground='red')
        self.tree.tag_configure('venda', foreground='black')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)
        scrollbar.pack(side=ttk.RIGHT, fill=ttk.Y)

    def setup_bottom_frame(self, main_frame):
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=ttk.X, pady=5)

        left_frame = ttk.Frame(bottom_frame)
        left_frame.pack(side=ttk.LEFT)
        ttk.Button(left_frame, 
                  text="NOVA VENDA (F2)", 
                  command=self.limpar_tudo, 
                  bootstyle="warning",
                  width=15).pack(side=ttk.LEFT, padx=2)

        right_frame = ttk.Frame(bottom_frame)
        right_frame.pack(side=ttk.RIGHT)
        self.total_label = ttk.Label(right_frame, 
                                   text="TOTAL: R$ 0,00", 
                                   font=("Helvetica", 14, "bold"),
                                   bootstyle="primary")
        self.total_label.pack(side=ttk.LEFT, padx=5)
        ttk.Button(right_frame, 
                  text="FINALIZAR VENDA (F5)", 
                  command=self.finalizar_venda, 
                  bootstyle="success",
                  width=20).pack(side=ttk.LEFT, padx=2)

    def update_time(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_time)

    @log_action("add_product")
    def adicionar_produto(self, event=None):
        codigo = self.codigo_entry.get().strip().lower()
        quantidade = self.quantidade_entry.get().strip()
        tipo = self.tipo_operacao.get()

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
            
            if tipo == "TROCA":
                subtotal = -subtotal

            self.produtos.append((codigo, descricao, quantidade, preco, subtotal, tipo))
            self.total += subtotal

            self.tree.insert("", "end", 
                           values=(codigo, descricao, quantidade, 
                                 f"R$ {abs(preco):.2f}", 
                                 f"R$ {abs(subtotal):.2f}",
                                 tipo),
                           tags=(tipo.lower(),))

            self.total_label.config(text=f"TOTAL: R$ {self.total:.2f}")

            self.codigo_entry.delete(0, "end")
            self.quantidade_entry.delete(0, "end")
            self.quantidade_entry.insert(0, "1")
            self.tipo_operacao.set("VENDA")
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
        
        if valores[5] == "TROCA":
            subtotal = -subtotal

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
        self.ticket_entry.delete(0, tk.END)

    def adicionar_troca(self):
        valor = simpledialog.askfloat("Trocas", "Valor da troca:")
        if valor and valor > 0:
            self.trocas += valor
            self.total -= valor
            self.total_label.config(text=f"TOTAL: R$ {self.total:.2f}")
            messagebox.showinfo("Troca registrada", f"Troca de R$ {valor:.2f} aplicada.")
        else:
            messagebox.showwarning("ATENÇÃO", "Valor inválido para troca!")

    def gerar_etiqueta_venda(self):
        try:
            imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
            draw = ImageDraw.Draw(imagem)
            
            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 35)
                fonte_texto = ImageFont.truetype("arial.ttf", 25)
            except:
                fonte_titulo = fonte_texto = ImageFont.load_default()

            y = self.MARGEM

            # Adicionar logo
            try:
                logo_path = get_resource_path("logo.png")
                if logo_path:
                    logo = Image.open(logo_path)
                    logo_width = 200
                    ratio = logo.size[1] / logo.size[0]
                    logo_height = int(logo_width * ratio)
                    logo = logo.resize((logo_width, logo_height))
                    x_pos = (self.LARGURA_PAPEL - logo_width) // 2
                    imagem.paste(logo, (x_pos, y), mask=logo if 'A' in logo.getbands() else None)
                    y += logo_height + 20
            except:
                draw.text((20, y), "AUSTRAL", font=fonte_titulo, fill="black")
                y += 50

            # Número do ticket se existir
            if self.ticket_entry.get().strip():
                draw.text((20, y), f"TICKET: #{self.ticket_entry.get().strip()}", 
                         font=fonte_titulo, fill="black")
                y += 40

            # Data e hora
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            draw.text((20, y), f"DATA: {data_hora}", font=fonte_texto, fill="black")
            y += 40

            # Produtos com códigos e indicação de troca
            draw.text((20, y), "PRODUTOS:", font=fonte_titulo, fill="black")
            y += 40

            for codigo, desc, qtd, preco, subtotal, tipo in self.produtos:
                # Define a cor baseada no tipo de operação
                cor = "red" if tipo == "TROCA" else "black"
                
                # Adiciona código do produto
                texto_codigo = f"COD: {codigo}"
                draw.text((20, y), texto_codigo, font=fonte_texto, fill=cor)
                y += 25
                
                # Descrição do produto com indicação do tipo
                texto_desc = f"{desc} ({tipo})"
                draw.text((20, y), texto_desc, font=fonte_texto, fill=cor)
                y += 25
                
                # Quantidade e valores
                texto_valor = f"{qtd}x R$ {abs(preco):.2f} = R$ {abs(subtotal):.2f}"
                draw.text((40, y), texto_valor, font=fonte_texto, fill=cor)
                y += 35

            if self.trocas > 0:
                draw.text((20, y), f"TROCAS: R$ {self.trocas:.2f}", font=fonte_titulo, fill="red")
                y += 40

            draw.text((20, y), f"TOTAL FINAL: R$ {self.total:.2f}", font=fonte_titulo, fill="black")

            temp_dir = tempfile.gettempdir()
            filename = f"recibo_venda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(temp_dir, filename)
            imagem.save(path)
            imagem.show()

        except Exception as e:
            messagebox.showerror("ERRO", f"Não foi possível gerar etiqueta: {str(e)}")

    def finalizar_venda(self):
        if not self.produtos:
            messagebox.showwarning("ATENÇÃO", "NENHUM PRODUTO NA LISTA!")
            return

        recibo = "=== AUSTRAL ===\n"
        if self.ticket_entry.get().strip():
            recibo += f"TICKET: #{self.ticket_entry.get().strip()}\n"
        recibo += f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        recibo += "=" * 40 + "\n\n"

        for codigo, desc, qtd, preco, subtotal, tipo in self.produtos:
            recibo += f"COD: {codigo}\n"
            recibo += f"{desc} ({tipo})\n"
            recibo += f"{qtd}x R$ {abs(preco):.2f} = R$ {abs(subtotal):.2f}\n\n"

        if self.trocas > 0:
            recibo += "=" * 40 + "\n"
            recibo += f"TROCAS: R$ {self.trocas:.2f}\n"

        recibo += "=" * 40 + "\n"
        recibo += f"TOTAL FINAL: R$ {self.total:.2f}\n"
        recibo += "=" * 40 + "\n"
        recibo += "\nOBRIGADO PELA PREFERÊNCIA!"

        messagebox.showinfo("VENDA FINALIZADA", recibo)
        self.gerar_etiqueta_venda()
        self.limpar_tudo()

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = PontoDeVendaApp(root)
    root.mainloop()
