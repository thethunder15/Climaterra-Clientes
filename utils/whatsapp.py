# utils/whatsapp.py
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMessageBox
import traceback

def enviar_mensagem_whatsapp(telefone, mensagem=None):
    try:
        # Verifica se o telefone é válido
        if not telefone or not isinstance(telefone, str):
            QMessageBox.warning(None, "Aviso", "Número de telefone inválido ou não fornecido.")
            return False
            
        # Remove qualquer caractere que não seja dígito
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        # Verifica se o telefone tem pelo menos 8 dígitos
        if len(telefone_limpo) < 8:
            QMessageBox.warning(None, "Aviso", "Número de telefone muito curto ou inválido.")
            return False
            
        # Constrói a URL usando o prefixo "https://wa.me/55" seguido do telefone limpo
        url = f"https://wa.me/55{telefone_limpo}"
        # Se você quiser incluir uma mensagem pré-definida (opcional), use:
        if mensagem:
            url = f"https://wa.me/55{telefone_limpo}?text={mensagem}"

        # Tenta abrir a URL
        return QDesktopServices.openUrl(QUrl(url))
    except Exception as e:
        # Captura qualquer erro e exibe uma mensagem amigável
        QMessageBox.critical(None, "Erro", f"Não foi possível abrir o WhatsApp: {str(e)}")
        traceback.print_exc()
        return False
