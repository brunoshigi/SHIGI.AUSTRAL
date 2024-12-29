import tkinter as tk
from tkinter import messagebox

def center_window(window, width=None, height=None):
    """Centraliza uma janela na tela"""
    window.update_idletasks()
    if width and height:
        window.geometry(f"{width}x{height}")
    w = window.winfo_width()
    h = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (w // 2)
    y = (window.winfo_screenheight() // 2) - (h // 2)
    window.geometry(f"+{x}+{y}")

def show_message(title, message, message_type="info"):
    """Mostra uma mensagem padronizada"""
    if message_type == "error":
        messagebox.showerror(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)
