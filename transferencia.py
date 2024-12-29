import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import tempfile
from lojas import lojas, estoque, matriz, servicos
import sys
from pathlib import Path
from config import ConfigManager
from logger import AustralLogger, log_action
from utils import FONT_LABEL, FONT_ENTRY, FONT_TITLE
from utils import setup_window_icon
from utils import UIHelper
from resource_manager import resource_manager



import sys
from pathlib import Path

def get_resource_path(filename: str) -> str:
    # Busca o recurso diretamente na raiz
    try:
        if getattr(sys, '_MEIPASS', False):  # Executável PyInstaller
            return os.path.join(sys._MEIPASS, filename)
        
        base_path = Path(__file__).resolve().parent
        resource_path = base_path / filename

        if resource_path.exists():
            return str(resource_path)
        raise FileNotFoundError(f"Recurso não encontrado: {filename}")
    except Exception as e:
        print(f"Erro ao localizar recurso {filename}: {e}")
        return None

class EtiquetaTransferenciaApp:
    def __init__(self, root):
        self.root = root   
        
        UIHelper.center_window(self.root, width=600, height=253)
        self.root.title("SISTEMA AUSTRAL - ETIQUETA DE TRANSFERÊNCIA INTERNA") 
        self.root.resizable(False, False) # Impede redimensionamento
        
        self.config = ConfigManager() # Gerenciador de configurações
        self.logger = AustralLogger() # Logger de ações
        
        # Configurações da impressora térmica (80mm)
        self.LARGURA_PAPEL = 500 # Aumentado para acomodar melhor o conteúdo
        self.LARGURA_IMPRESSAO = 470 # Aumentado para acomodar melhor o conteúdo
        self.ALTURA_ETIQUETA = 680 # Aumentado para acomodar melhor o conteúdo
        self.MARGEM = 10 # Margem interna
        
        self.setup_ui()
        setup_window_icon(self.root)
        self.load_last_values()

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Container principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior - título
        title_label = ttk.Label(
            main_frame,
            text="ETIQUETA DE TRANSFERÊNCIA",
            font=FONT_TITLE,
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20)) # Espaçamento inferior

        # Frame para as lojas
        shipping_frame = ttk.Frame(main_frame)
        shipping_frame.pack(fill=tk.X, pady=(0, 20))
        shipping_frame.columnconfigure(0, weight=1)
        shipping_frame.columnconfigure(1, weight=1)

        # Frame Origem (lado esquerdo)
        origem_frame = ttk.LabelFrame(shipping_frame, text="FILIAL ORIGEM", padding="10")
        origem_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.origem_var = tk.StringVar()
        self.origem_combo = ttk.Combobox(
            origem_frame,
            textvariable=self.origem_var,
            values=[loja["loja"] for loja in lojas],
            font=FONT_ENTRY,
            state="readonly"
        )
        self.origem_combo.pack(fill=tk.X)

        # Frame Destino (lado direito)
        destino_frame = ttk.LabelFrame(shipping_frame, text="FILIAL DESTINO", padding="10")
        destino_frame.grid(row=0, column=1, sticky="ew")

        self.destino_var = tk.StringVar()
        
        # Criando lista completa de destinos
        destinos = []
        destinos.extend([loja["loja"] for loja in lojas])  # Adiciona lojas
        destinos.extend([loja["loja"] for loja in estoque])  # Adiciona estoque
        destinos.extend([loja["loja"] for loja in matriz])   # Adiciona matriz
        destinos.extend([loja["loja"] for loja in servicos])  # Adiciona serviços
        
        self.destino_combo = ttk.Combobox(
            destino_frame,
            textvariable=self.destino_var,
            values=destinos,
            font=FONT_ENTRY,
            state="readonly"
        )
        self.destino_combo.pack(fill=tk.X)

        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(
            button_frame,
            text="LIMPAR CAMPOS",
            command=self.limpar_campos,
            style="Danger.TButton",
            width=25
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="GERAR ETIQUETA",
            command=self.gerar_etiqueta,
            style="Primary.TButton",
            width=25
        ).pack(side=tk.RIGHT, padx=5)

    def get_info_from_all_lists(self, loja_name):
        """Busca informações da loja em todas as listas"""
        for lista in [lojas, estoque, matriz, servicos]:
            for loja in lista:
                if loja["loja"] == loja_name:
                    return loja
        return None

    def criar_imagem_etiqueta(self):
        """Cria a imagem da etiqueta para impressora térmica"""
        try:
            imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
            draw = ImageDraw.Draw(imagem)
            
            # Define as fontes com tamanhos diferentes para origem e destino
            try:
                fonte_titulo_destino = ImageFont.truetype("arial.ttf", 35)  # Fonte maior para destino
                fonte_titulo_origem = ImageFont.truetype("arial.ttf", 30)   # Fonte menor para origem
                fonte_texto_destino = ImageFont.truetype("arial.ttf", 40)   # Texto destino maior
                fonte_texto_origem = ImageFont.truetype("arial.ttf", 30)    # Texto origem menor
                fonte_info = ImageFont.truetype("arial.ttf", 30)            # Informações gerais
                fonte_alerta = ImageFont.truetype("arial.ttf", 38)          # Alertas
            except:
                fonte_titulo_destino = fonte_titulo_origem = fonte_texto_destino = fonte_texto_origem = fonte_info = fonte_alerta = ImageFont.load_default()

            y = self.MARGEM

            # Box e Interfone (se for estoque) - No topo se aplicável
            destino_info = self.get_info_from_all_lists(self.destino_var.get())
            if destino_info and ("ESTOQUE" in destino_info["loja"] or "BOX" in destino_info.get("piso", "")):
                box_text = "BOX 20011\nTOCAR INTERFONE 0525"
                # Centralizar o texto de alerta
                box_width = draw.textlength(box_text.split('\n')[0], fonte_alerta)
                x_pos = (self.LARGURA_PAPEL - box_width) // 2
                lines = box_text.split('\n')
                for line in lines:
                    w = draw.textlength(line, fonte_alerta)
                    x = (self.LARGURA_PAPEL - w) // 2
                    draw.text((x, y), line, font=fonte_alerta, fill="red")
                    y += 40
                y += 20

            # Logo Austral
            try:
                logo_path = get_resource_path("logo.png")
                if logo_path:
                    logo = Image.open(logo_path)
                # Redimensiona o logo para um tamanho adequado
                logo_width = 200
                ratio = logo.size[1] / logo.size[0]
                logo_height = int(logo_width * ratio)
                logo = logo.resize((logo_width, logo_height))
                # Centraliza o logo horizontalmente
                x_pos = (self.LARGURA_PAPEL - logo_width) // 2
                imagem.paste(logo, (x_pos, y), mask=logo if 'A' in logo.getbands() else None)
                y += logo_height + 20
            except Exception as e:
                UIHelper.show_message(
                    "AVISO",
                    "Logo não encontrado. Usando texto como alternativa.",
                    "warning"
                )
                draw.text((self.MARGEM, y), "Austral", font=fonte_titulo_origem, fill="black")
                y += 50

            # Origem (fonte menor)
            draw.text((self.MARGEM, y), "FILIAL ORIGEM:", font=fonte_titulo_origem, fill="blue")
            y += 30
            origem_info = self.get_info_from_all_lists(self.origem_var.get())
            if origem_info:
                draw.text((self.MARGEM, y), origem_info["loja"], font=fonte_texto_origem, fill="black")
                y += 35

            # Linha divisória
            y += 10
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=1)
            y += 20

            # Destino (fonte maior para destaque)
            draw.text((self.MARGEM, y), "FILIAL DESTINO:", font=fonte_titulo_destino, fill="blue")
            y += 40
            if destino_info:
                draw.text((self.MARGEM, y), destino_info["loja"], font=fonte_texto_destino, fill="black")
                y += 40
                draw.text((self.MARGEM, y), destino_info["endereco"], font=fonte_info, fill="black")
                y += 30
                draw.text((self.MARGEM, y), destino_info["bairro_cidade_estado_cep"], font=fonte_info, fill="black")
                y += 30
                if destino_info.get("piso"):
                    draw.text((self.MARGEM, y), destino_info["piso"], font=fonte_info, fill="black")
                    y += 30
                if destino_info.get("telefone"):
                    draw.text((self.MARGEM, y), f"Tel: {destino_info['telefone']}", font=fonte_info, fill="black")
                    y += 30

            # Data e Hora
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            draw.text((self.MARGEM, y), data_hora, font=fonte_info, fill="black")

            # Se for estoque, adiciona o alerta novamente no rodapé
            if destino_info and ("ESTOQUE" in destino_info["loja"] or "BOX" in destino_info.get("piso", "")):
                y = self.ALTURA_ETIQUETA - 50
                linha = "TOCAR INTERFONE 0525"
                w = draw.textlength(linha, fonte_alerta)
                x = (self.LARGURA_PAPEL - w) // 2
                draw.text((x, y), linha, font=fonte_alerta, fill="red")

            return imagem
            
        except Exception as e:
            UIHelper.show_message(
                "ERRO",
                f"Erro ao criar imagem da etiqueta: {str(e)}",
                "error"
            )
            return None

    def validar_campos(self):
        """Valida os campos antes de gerar a etiqueta"""
        if not self.origem_var.get():
            UIHelper.show_message(
                "ATENÇÃO",
                "Selecione a filial de origem!",
                "warning"
            )
            return False
            
        if not self.destino_var.get():
            UIHelper.show_message(
                "ATENÇÃO",
                "Selecione a filial de destino!",
                "warning"
            )
            return False
            
        if self.origem_var.get() == self.destino_var.get():
            UIHelper.show_message(
                "ATENÇÃO",
                "Origem e destino não podem ser iguais!",
                "warning"
            )
            return False
            
        return True

    @log_action("print_transfer_label")
    def gerar_etiqueta(self):
        """Gera e mostra a etiqueta"""
        if not self.validar_campos():
            return

        try:
            imagem = self.criar_imagem_etiqueta()
            if imagem:
                # Salva em arquivo temporário
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"etiqueta_transferencia_{timestamp}.png"
                temp_path = os.path.join(temp_dir, filename)
                imagem.save(temp_path)
                
                # Mostra a imagem
                imagem.show()
                
                self.save_last_values()
                UIHelper.show_message(
                    "SUCESSO",
                    "Etiqueta gerada com sucesso!",
                    "info"
                )
            
        except Exception as e:
            UIHelper.show_message(
                "ERRO",
                f"Erro ao gerar etiqueta: {str(e)}",
                "error"
            )

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        try:
            self.origem_var.set('')
            self.destino_var.set('')
        except Exception as e:
            UIHelper.show_message(
                "ERRO",
                f"Erro ao limpar campos: {str(e)}",
                "error"
            )

    def save_last_values(self):
        """Salva os últimos valores utilizados"""
        try:
            self.config.set('etiqueta_transferencia.last_values', {
                'origem': self.origem_var.get(),
                'destino': self.destino_var.get()
            })
        except Exception as e:
            UIHelper.show_message(
                "ERRO",
                f"Erro ao salvar valores: {str(e)}",
                "error"
            )

    def load_last_values(self):
        """Carrega os últimos valores utilizados"""
        try:
            last_values = self.config.get('etiqueta_transferencia.last_values', {})
            if last_values:
                self.origem_var.set(last_values.get('origem', ''))
                self.destino_var.set(last_values.get('destino', ''))
        except Exception as e:
            UIHelper.show_message(
                "ERRO",
                f"Erro ao carregar valores: {str(e)}",
                "error"
            )

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = EtiquetaTransferenciaApp(root)
    root.mainloop()