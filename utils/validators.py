# utils/validators.py
import re

def validar_cpf_cnpj(documento: str) -> bool:
    # Remove caracteres não numéricos
    doc = re.sub(r'\D', '', documento)
    
    # Validação de CPF
    if len(doc) == 11:
        # Implementação de validação de CPF
        soma = sum(int(doc[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        soma = sum(int(doc[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return doc[-2:] == f'{digito1}{digito2}'
    
    # Validação de CNPJ
    elif len(doc) == 14:
        # Implementação de validação de CNPJ
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        
        soma1 = sum(int(doc[i]) * pesos1[i] for i in range(12))
        resto1 = soma1 % 11
        digito1 = 0 if resto1 < 2 else 11 - resto1
        
        soma2 = sum(int(doc[i]) * pesos2[i] for i in range(13))
        resto2 = soma2 % 11
        digito2 = 0 if resto2 < 2 else 11 - resto2
        
        return doc[-2:] == f'{digito1}{digito2}'
    
    return False

def validar_email(email: str) -> bool:
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None