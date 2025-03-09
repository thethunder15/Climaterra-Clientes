# utils/whatsapp.py
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

def enviar_mensagem_whatsapp(telefone, mensagem=None):
    # Remove qualquer caractere que não seja dígito
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    # Constrói a URL usando o prefixo "https://wa.me/55" seguido do telefone limpo
    url = f"https://wa.me/55{telefone_limpo}"
    # Se você quiser incluir uma mensagem pré-definida (opcional), use:
    # url = f"https://wa.me/55{telefone_limpo}?text={mensagem}"

    QDesktopServices.openUrl(QUrl(url))
