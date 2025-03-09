# database/database.py
import sqlite3
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_name='clientes.db'):
        self.conn = sqlite3.connect(db_name)
        self.criar_tabela()

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                cpf_cnpj TEXT,
                email TEXT,
                periodo_assinatura INTEGER,
                ultimo_pagamento DATE,
                vencimento DATE,
                data_aviso DATE,
                avisado BOOLEAN,
                status TEXT,
                estado TEXT,
                cidade TEXT,
                observacao TEXT,
                comprovante TEXT
            )
        ''')

        # Verifica se a coluna 'comprovante' existe
        cursor.execute("PRAGMA table_info(clientes)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'comprovante' not in column_names:
            # Adiciona a coluna 'comprovante' se ela não existir
            cursor.execute('ALTER TABLE clientes ADD COLUMN comprovante TEXT')
            self.conn.commit()

        self.conn.commit()

    def adicionar_cliente(self, cliente: Tuple) -> int:
        cursor = self.conn.cursor()
        query = '''
            INSERT INTO clientes (
                nome, telefone, cpf_cnpj, email, periodo_assinatura, 
                ultimo_pagamento, vencimento, data_aviso, avisado, 
                status, estado, cidade, observacao, comprovante
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, cliente)
        self.conn.commit()
        return cursor.lastrowid

    def listar_clientes(self) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        return cursor.fetchall()

    def atualizar_cliente(self, cliente):
        try:
            if len(cliente) != 15:
                raise ValueError(f"Número incorreto de parâmetros. Esperado 15, recebido {len(cliente)}")

            query = """
        UPDATE clientes 
        SET 
            nome = ?,
            telefone = ?,
            cpf_cnpj = ?,
            email = ?,
            periodo_assinatura = ?,
            ultimo_pagamento = ?,
            vencimento = ?,
            data_aviso = ?,
            avisado = ?,
            status = ?,
            estado = ?,
            cidade = ?,
            observacao = ?,
            comprovante = ?
        WHERE id = ?
        """
            cursor = self.conn.cursor()
            cursor.execute(query, cliente)
            self.conn.commit()

        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Erro de banco de dados: {e}")
            raise
        except Exception as e:
            self.conn.rollback()
            print(f"Erro inesperado: {e}")
            raise

    def remover_cliente(self, cliente_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        self.conn.commit()

    def fechar_conexao(self):
        self.conn.close()

    def atualizar_status_cliente(self, cliente_id: int, novo_status: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE clientes
            SET status = ?
            WHERE id = ?
        ''', (novo_status, cliente_id))
        self.conn.commit()

    def pesquisar_clientes(self, criterio: str, valores: list) -> List[Tuple]:
        cursor = self.conn.cursor()

        mapeamento = {
            'Nome': 'nome',
            'Telefone': 'telefone',
            'CPF/CNPJ': 'cpf_cnpj',
            'E-mail': 'email',
            'Vencimento (DD/MM/AAAA)': 'vencimento',
            'Status': 'status',
            'Estado': 'estado'
        }

        coluna = mapeamento.get(criterio)
        if not coluna or not valores:
            return []

        try:
            # Busca parcial para textos
            if criterio in ['Nome', 'Telefone', 'CPF/CNPJ', 'E-mail']:
                query = f"SELECT * FROM clientes WHERE {coluna} LIKE ?"
                cursor.execute(query, (f'%{valores[0]}%',))

            # Data exata
            elif criterio == 'Vencimento (DD/MM/AAAA)':
                data = datetime.strptime(valores[0], "%d/%m/%Y").strftime("%Y-%m-%d")
                cursor.execute(f"SELECT * FROM clientes WHERE {coluna} = ?", (data,))

            # Seleção múltipla
            else:
                placeholders = ','.join(['?'] * len(valores))
                cursor.execute(f"SELECT * FROM clientes WHERE {coluna} IN ({placeholders})", valores)

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro na pesquisa: {e}")
            return []

    def obter_cliente_por_id(self, cliente_id: int) -> Optional[dict]:
        """
        Obtém um cliente pelo ID e retorna como dicionário.

        Args:
            cliente_id (int): ID do cliente a ser buscado

        Returns:
            Optional[dict]: Dicionário com os dados do cliente ou None se não encontrado
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
            cliente_tupla = cursor.fetchone()

            if not cliente_tupla:
                return None

            # Obter os nomes das colunas da tabela
            cursor.execute("PRAGMA table_info(clientes)")
            colunas = [info[1] for info in cursor.fetchall()]

            # Criar um dicionário mapeando cada nome de coluna ao valor correspondente
            cliente_dict = {colunas[i]: cliente_tupla[i] for i in range(len(colunas))}

            return cliente_dict
        except sqlite3.Error as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return None

    # Exemplo de implementação na classe Database
    def atualizar_aviso_cliente(self, cliente_id, data_aviso, avisado):
        try:
            cursor = self.conn.cursor()
            sql = "UPDATE clientes SET data_aviso = ?, avisado = ? WHERE id = ?"
            cursor.execute(sql, (data_aviso, avisado, cliente_id))
            self.conn.commit()
        except Exception as e:
            print("Erro ao atualizar aviso:", e)
            raise
