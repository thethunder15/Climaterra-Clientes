# status_helper.py
from datetime import datetime

def calcular_status(vencimento, hoje=None) -> str:
    """Calcula o status considerando múltiplos formatos de data"""
    if hoje is None:
        hoje = datetime.now().date()

    # Converte strings para date
    if isinstance(vencimento, str):
        try:
            # Tenta formato ISO (YYYY-MM-DD)
            vencimento = datetime.strptime(vencimento, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Tenta formato brasileiro (DD/MM/YYYY)
                vencimento = datetime.strptime(vencimento, "%d/%m/%Y").date()
            except:
                return "Data inválida"

    dias_restantes = (vencimento - hoje).days

    if dias_restantes < 0:
        return "Inadimplente"
    elif dias_restantes <= 5:
        return "Expirando"
    else:
        return "Em dia"