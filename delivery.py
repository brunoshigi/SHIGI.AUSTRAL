import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk  # Import correto do ttkbootstrap
from ttkbootstrap.constants import *
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import tempfile
from config import ConfigManager
from logger import AustralLogger, log_action
from lojas import lojas
from utils import setup_window_icon
from utils import UIHelper
from utils import FONT_LABEL, FONT_ENTRY


class EtiquetaClientesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ETIQUETA PARA DELIVERY")
        self.config = ConfigManager()
        self.logger = AustralLogger()
        self.endereco_completo = {}
        
        # Configurações da impressora térmica (80mm)
        self.LARGURA_PAPEL = 800
        self.LARGURA_IMPRESSAO = 720
        self.ALTURA_ETIQUETA = 960
        self.MARGEM = 40

        self.setup_ui()
        setup_window_icon(self.root)
        self.load_last_values()
        
        # Define um tamanho inicial mais compacto para a janela
        self.root.geometry("500x550")

    def setup_ui(self):
        """Configura a interface compacta com foco em delivery"""
        # Container principal com padding reduzido
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame da loja mais compacto
        loja_frame = ttk.LabelFrame(main_frame, text="LOJA", padding="5")# Removido padding superior e reduzido padding inferior para 5 pixels 
        loja_frame.pack(fill=tk.X, pady=(0, 5)) # Removido padding superior  e reduzido padding inferior para 5 pixels 

        self.loja_var = tk.StringVar()
        self.loja_combo = ttk.Combobox(
            loja_frame,
            textvariable=self.loja_var,
            values=[loja["loja"] for loja in lojas if "A/C" not in loja["loja"]],
            font=("Helvetica", 10),
            width=35,
            state="readonly"
        )
        self.loja_combo.pack(fill=tk.X, padx=2, pady=2)

        # Frame de informações do cliente
        info_frame = ttk.LabelFrame(main_frame, text="DADOS DO CLIENTE", padding="5")
        info_frame.pack(fill=tk.X, pady=5)
        info_frame.columnconfigure(1, weight=1)

        # Grid de campos com espaçamento reduzido
        campos = [
            ("CLIENTE:", self.create_entry),
            ("CEP:", lambda p: self.create_entry(p, '<FocusOut>', self.consultar_cep_evento)),
            ("NUMERO:", self.create_entry),
            ("COMPLEMENTO:", self.create_entry),
            ("REFERENCIA:", self.create_entry)  # Removido acento de "REFERÊNCIA"
        ]

        for i, (label_text, create_func) in enumerate(campos):
            ttk.Label(
                info_frame,
                text=label_text,
                font=("Helvetica", 10)
            ).grid(row=i, column=0, sticky='w', padx=2, pady=2)
            
            entry = create_func(info_frame)
            entry.grid(row=i, column=1, sticky='ew', padx=2, pady=2)
            
            # Converter o nome do atributo para minúsculo e sem acentos
            attr_name = label_text.lower().replace(':', '').replace('ú', 'u').replace('ê', 'e').replace('í', 'i').replace('á', 'a')
            setattr(self, f"{attr_name}_entry", entry)

        # Preview mais compacto
        preview_frame = ttk.LabelFrame(main_frame, text="PREVIEW", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.preview_text = tk.Text(
            preview_frame,
            height=6,
            font=("Courier New", 10),
            wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.preview_text.config(state='disabled')

        # Frame de botões mais compacto
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="LIMPAR",
            command=self.limpar_campos,
            style="Secondary.TButton",
            width=12
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="IMPRIMIR",
            command=self.gerar_etiqueta,
            style="Primary.TButton",
            width=12
        ).pack(side=tk.RIGHT, padx=2)

    def create_entry(self, parent, bind_event=None, bind_func=None):
        """Cria um campo de entrada padronizado"""
        entry = ttk.Entry(parent, font=("Helvetica", 10))
        if bind_event and bind_func:
            entry.bind(bind_event, bind_func)
        return entry

    def criar_imagem_etiqueta(self):
        """Cria a imagem da etiqueta otimizada para impressora térmica"""
        imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
        draw = ImageDraw.Draw(imagem)

        try:
            # Aumentando o tamanho das fontes
            fonte_titulo = ImageFont.truetype("arial.ttf", 45)  # Era 30
            fonte_nome = ImageFont.truetype("arial.ttf", 60)    # Era 45
            fonte_endereco = ImageFont.truetype("arial.ttf", 45) # Era 35
            fonte_info = ImageFont.truetype("arial.ttf", 35)    # Era 25
        except:
            fonte_titulo = fonte_nome = fonte_endereco = fonte_info = ImageFont.load_default()

        y = self.MARGEM

        # Linha superior
        draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=3)
        y += 25  # Aumentado de 10

        # Data e hora
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        draw.text((self.MARGEM, y), f"DATA/HORA: {data_hora}", fill="black", font=fonte_info)
        y += 50  # Aumentado de 40

        # Nome da loja
        loja = self.loja_var.get().upper()
        draw.text((self.MARGEM, y), loja, fill="black", font=fonte_titulo)
        y += 60  # Aumentado de 50

        # Linha divisória
        draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=2)
        y += 25  # Aumentado de 20

        # Nome do cliente em destaque
        nome_cliente = self.cliente_entry.get().upper()
        draw.text((self.MARGEM, y), "CLIENTE:", fill="black", font=fonte_titulo)
        y += 50  # Aumentado de 40
        draw.text((self.MARGEM, y), nome_cliente, fill="black", font=fonte_nome)
        y += 70  # Aumentado de 60

        # Linha divisória
        draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=2)
        y += 35  # Aumentado de 20

        # Endereço
        if self.endereco_completo:
            # Logradouro e número
            endereco = f"{self.endereco_completo['logradouro'].upper()}, {self.numero_entry.get().upper()}"
            linhas_endereco = self.ajustar_texto_largura(draw, endereco, fonte_endereco, self.LARGURA_IMPRESSAO - 2 * self.MARGEM)
            for linha in linhas_endereco:
                draw.text((self.MARGEM, y), linha, fill="black", font=fonte_endereco)
                y += draw.textbbox((0, 0), linha, font=fonte_endereco)[3] + 5  # Ajuste de espaçamento

            # Complemento
            if self.complemento_entry.get().strip():
                linhas_complemento = self.ajustar_texto_largura(draw, self.complemento_entry.get().strip().upper(), fonte_endereco, self.LARGURA_IMPRESSAO - 2 * self.MARGEM)
                for linha in linhas_complemento:
                    draw.text((self.MARGEM, y), linha, fill="black", font=fonte_endereco)
                    y += draw.textbbox((0, 0), linha, font=fonte_endereco)[3] + 5

            # Bairro
            linhas_bairro = self.ajustar_texto_largura(draw, self.endereco_completo['bairro'].upper(), fonte_endereco, self.LARGURA_IMPRESSAO - 2 * self.MARGEM)
            for linha in linhas_bairro:
                draw.text((self.MARGEM, y), linha, fill="black", font=fonte_endereco)
                y += draw.textbbox((0, 0), linha, font=fonte_endereco)[3] + 5

            # Cidade e Estado
            cidade_estado = f"{self.endereco_completo['localidade'].upper()} - {self.endereco_completo['uf'].upper()}"
            linhas_cidade_estado = self.ajustar_texto_largura(draw, cidade_estado, fonte_endereco, self.LARGURA_IMPRESSAO - 2 * self.MARGEM)
            for linha in linhas_cidade_estado:
                draw.text((self.MARGEM, y), linha, fill="black", font=fonte_endereco)
                y += draw.textbbox((0, 0), linha, font=fonte_endereco)[3] + 5

            # CEP
            draw.text((self.MARGEM, y), f"CEP: {self.endereco_completo['cep']}", fill="black", font=fonte_endereco)
            y += draw.textbbox((0, 0), "CEP:", font=fonte_endereco)[3] + 25
            

        # Linha divisória
        draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=2)
        y += 30  # Aumentado de 20

        # Referência
        if self.referencia_entry.get().strip():
            draw.text((self.MARGEM, y), "REFERÊNCIA:", fill="black", font=fonte_titulo)
            y += 45  # Aumentado de 35
            linhas_referencia = self.ajustar_texto_largura(draw, self.referencia_entry.get().strip().upper(), fonte_endereco, self.LARGURA_IMPRESSAO - 2 * self.MARGEM)
            for linha in linhas_referencia:
                draw.text((self.MARGEM, y), linha, fill="black", font=fonte_endereco)
                y += draw.textbbox((0, 0), linha, font=fonte_endereco)[3] + 5

        # Linha inferior
        y = self.ALTURA_ETIQUETA - self.MARGEM - 15  # Ajustado de 10
        draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=3)

        return imagem

    def consultar_cep_evento(self, event):
        """Consulta o CEP quando o campo perde o foco"""
        cep = self.cep_entry.get().replace('-', '').strip()
        if len(cep) == 8:
            self.endereco_completo = self.consultar_cep(cep)
            if self.endereco_completo:
                self.atualizar_preview()
            else:
                self.atualizar_preview("CEP não encontrado")

    def consultar_cep(self, cep):
        """Consulta o CEP usando a API ViaCEP"""
        try:
            response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
            response.raise_for_status()
            dados = response.json()
            return None if 'erro' in dados else dados
        except:
            return None

    def atualizar_preview(self, mensagem=None):
        """Atualiza o preview da etiqueta"""
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        if mensagem:
            self.preview_text.insert(tk.END, mensagem)
            self.preview_text.config(state='disabled')
            return

        if not self.endereco_completo:
            self.preview_text.config(state='disabled')
            return

        # Monta o preview
        preview = []
        preview.append(f"LOJA: {self.loja_var.get().upper()}")  # Convertendo para maiúsculas
        preview.append("-" * 50)
        preview.append(f"CLIENTE: {self.cliente_entry.get().upper()}")  # Convertendo para maiúsculas
        preview.append("-" * 50)
        
        numero = self.numero_entry.get().strip()
        complemento = self.complemento_entry.get().strip()
        
        preview.append(f"{self.endereco_completo['logradouro'].upper()}, {numero}")
        if complemento:
            preview.append(complemento.upper())
        preview.append(f"{self.endereco_completo['bairro'].upper()}")
        preview.append(f"{self.endereco_completo['localidade'].upper()} - {self.endereco_completo['uf'].upper()}")
        preview.append(f"CEP: {self.endereco_completo['cep']}")
        
        if self.referencia_entry.get().strip():
            preview.append("-" * 50)
            preview.append(f"REFERÊNCIA: {self.referencia_entry.get().upper()}")  # Convertendo para maiúsculas

        self.preview_text.insert(tk.END, "\n".join(preview))
        self.preview_text.config(state='disabled')

    @log_action("print_delivery_label")
    def gerar_etiqueta(self):
        """Gera e mostra a etiqueta"""
        if not self.validar_campos():
            return

        try:
            imagem = self.criar_imagem_etiqueta()
            
            # Salva em arquivo temporário
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"etiqueta_delivery_{timestamp}.png"
            temp_path = os.path.join(temp_dir, filename)
            imagem.save(temp_path)
            
            # Mostra a imagem em vez de imprimir
            imagem.show()
            
            self.save_last_values()
            messagebox.showinfo("SUCESSO", "Etiqueta gerada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("ERRO", f"Erro ao gerar etiqueta: {str(e)}")

    def validar_campos(self):
        """Valida os campos antes de gerar a etiqueta"""
        if not self.loja_var.get():
            messagebox.showwarning("ATENÇÃO", "Selecione uma loja!")
            return False
        if not self.cliente_entry.get().strip():
            messagebox.showwarning("ATENÇÃO", "Digite o nome do cliente!")
            return False
        if not self.endereco_completo:
            messagebox.showwarning("ATENÇÃO", "Consulte um CEP válido!")
            return False
        if not self.numero_entry.get().strip():
            messagebox.showwarning("ATENÇÃO", "Digite o número do endereço!")
            return False
        return True

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.loja_var.set('')
        self.cliente_entry.delete(0, tk.END)
        self.cep_entry.delete(0, tk.END)
        self.numero_entry.delete(0, tk.END)
        self.complemento_entry.delete(0, tk.END)
        self.referencia_entry.delete(0, tk.END)
        self.endereco_completo = {}
        self.atualizar_preview()

    def save_last_values(self):
        """Salva os últimos valores utilizados"""
        self.config.set('etiqueta_clientes.last_values', {
            'loja': self.loja_var.get()
        })

    def load_last_values(self):
        """Carrega os últimos valores utilizados"""
        last_values = self.config.get('etiqueta_clientes.last_values', {})
        if last_values:
            self.loja_var.set(last_values.get('loja', ''))

    @staticmethod
    def ajustar_texto_largura(draw, texto: str, fonte, largura_maxima: int) -> list:
        """Ajusta o texto para caber na largura da impressora térmica"""
        palavras = texto.split()
        linhas = []
        linha_atual = []
        largura_atual = 0

        for palavra in palavras:
            largura_palavra = draw.textlength(palavra + " ", font=fonte)
            
            if largura_atual + largura_palavra <= largura_maxima:
                linha_atual.append(palavra)
                largura_atual += largura_palavra
            else:
                if linha_atual:
                    linhas.append(' '.join(linha_atual))
                linha_atual = [palavra]
                largura_atual = largura_palavra

        if linha_atual:
            linhas.append(' '.join(linha_atual))

        return linhas

if __name__ == "__main__":
    # Opção 1: Usando tkinter padrão
    root = tk.Tk()
    # Configurar tema aqui se necessário
    
    app = EtiquetaClientesApp(root)
    root.mainloop()

