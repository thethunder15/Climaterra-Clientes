from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QComboBox, QDateEdit,
                             QCheckBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog,
                             QFormLayout, QListWidget, QFileDialog, QScrollArea, QApplication
                             )
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import datetime, timedelta
from utils.status_helper import calcular_status
from database.database import Database
from utils.validators import validar_cpf_cnpj, validar_email
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import traceback
import os
import hashlib
import shutil
import sys
from utils.whatsapp import enviar_mensagem_whatsapp
from utils.directory_helper import ensure_comprovantes_dir

# Get the base path for resources
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Get the comprovantes directory path
COMPROVANTES_DIR = ensure_comprovantes_dir()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Climaterra - Gerenciamento de Clientes')
        self.resize(1000, 600)

        self.setWindowIcon(QIcon(get_resource_path('icones/icone.png')))

        # Inicializa o banco de dados
        self.database = Database()

        # Cria a interface gráfica
        self.criar_interface()

        # Recalcula os status e atualiza a tabela
        self.recalcular_status_global()
        self.atualizar_tabela()

        # **Aqui garantimos que a janela será maximizada ao iniciar**
        self.showMaximized()

    def criar_interface(self):
        """Cria todos os componentes da interface gráfica."""
        widget_central = QWidget()
        layout_principal = QVBoxLayout()

        # Tabela de clientes
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.horizontalHeader().setSectionsMovable(True)
        self.tabela_clientes.setColumnCount(15)  # Removido o ID
        self.tabela_clientes.setHorizontalHeaderLabels([
            'ID','Nome', 'Telefone', 'CPF/CNPJ', 'E-mail', 'Período',
            'Último Pagamento', 'Vencimento', 'Data Aviso', 'Avisado',
            'Status', 'Estado', 'Municipio', 'Observação', 'Comprovante'
        ])
        self.tabela_clientes.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8f8f8;
                selection-background-color: #e0f0ff;
            }
        """)

        # Oculta a coluna do ID
        self.tabela_clientes.setColumnHidden(0, True)

        # Habilita a ordenação ao clicar nos rótulos das colunas
        self.tabela_clientes.setSortingEnabled(True)

        # Botões de ação
        layout_botoes = QHBoxLayout()

        botao_adicionar = QPushButton('Adicionar')
        botao_adicionar.setIcon(QIcon(get_resource_path('icones/add.png')))
        botao_adicionar.setIconSize(QSize(20, 20))
        botao_adicionar.clicked.connect(self.adicionar_cliente)

        botao_editar = QPushButton('Editar')
        botao_editar.setIcon(QIcon(get_resource_path('icones/edit.png')))
        botao_editar.setIconSize(QSize(20, 20))
        botao_editar.clicked.connect(self.editar_cliente)

        botao_remover = QPushButton('Remover')
        botao_remover.setIcon(QIcon(get_resource_path('icones/delete.png')))
        botao_remover.setIconSize(QSize(20, 20))
        botao_remover.clicked.connect(self.remover_cliente)

        botao_avisar = QPushButton('Avisar')
        botao_avisar.setIcon(QIcon(get_resource_path('icones/aviso.png')))
        botao_avisar.setIconSize(QSize(20, 20))
        botao_avisar.clicked.connect(self.avisar_cliente)

        botao_pesquisar = QPushButton('Pesquisar')
        botao_pesquisar.setIcon(QIcon(get_resource_path('icones/search.png')))
        botao_pesquisar.setIconSize(QSize(20, 20))
        botao_pesquisar.clicked.connect(self.abrir_janela_pesquisa)

        botao_listar = QPushButton('Listar Todos')
        botao_listar.setIcon(QIcon(get_resource_path('icones/refresh.png')))
        botao_listar.setIconSize(QSize(20, 20))
        botao_listar.clicked.connect(self.atualizar_tabela)

        botao_renovar = QPushButton('Renovação')
        botao_renovar.setIcon(QIcon(get_resource_path('icones/money.png')))
        botao_renovar.setIconSize(QSize(20, 20))
        botao_renovar.clicked.connect(self.abrir_renovacao)

        botao_comprovante = QPushButton('Ver Comprovante')
        botao_comprovante.setIcon(QIcon(get_resource_path('icones/request_quote.png')))
        botao_comprovante.setIconSize(QSize(20, 20))
        botao_comprovante.clicked.connect(self.ver_comprovante)

        botao_relatorio = QPushButton('Relatório')
        botao_relatorio.setIcon(QIcon(get_resource_path('icones/chart.png')))
        botao_relatorio.setIconSize(QSize(20, 20))
        botao_relatorio.clicked.connect(self.abrir_janela_relatorio)

        botao_importar = QPushButton('Importar CSV')
        botao_importar.setIcon(QIcon(get_resource_path('icones/csv.png')))
        botao_importar.setIconSize(QSize(20, 20))
        botao_importar.clicked.connect(self.importar_csv)

        layout_botoes.addWidget(botao_adicionar)
        layout_botoes.addWidget(botao_editar)
        layout_botoes.addWidget(botao_remover)
        layout_botoes.addWidget(botao_avisar)
        layout_botoes.addWidget(botao_pesquisar)
        layout_botoes.addWidget(botao_listar)
        layout_botoes.addWidget(botao_renovar)
        layout_botoes.addWidget(botao_comprovante)
        layout_botoes.addWidget(botao_relatorio)
        layout_botoes.addWidget(botao_importar)

        layout_principal.addWidget(self.tabela_clientes)
        layout_principal.addLayout(layout_botoes)

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        self.atualizar_tabela()

    def atualizar_tabela(self):
        try:
            clientes = self.database.listar_clientes()
            self.tabela_clientes.setRowCount(len(clientes))
            self.tabela_clientes.setColumnCount(15)  # Mantenha as 15 colunas
            headers = [
                'ID','Nome', 'Telefone', 'CPF/CNPJ', 'E-mail', 'Período',
                'Último Pagamento', 'Vencimento', 'Data Aviso', 'Avisado',
                'Status', 'Estado', 'Municipio', 'Observação', 'Comprovante'
            ]
            self.tabela_clientes.setHorizontalHeaderLabels(headers)
            self.tabela_clientes.setColumnHidden(0, True)  # ID permanece oculto

            # Índices das colunas que devem ter alinhamento à esquerda
            colunas_alinhamento_esquerda = [1, 4, 14]  # Nome, E-mail, Observação

            for linha, cliente in enumerate(clientes):
                for coluna in range(15):  # Itera todas as 15 colunas
                    if coluna == 0:  # ID (coluna 0, oculta)
                        valor = str(cliente[0])
                        item = QTableWidgetItem(valor)
                        self.tabela_clientes.setItem(linha, 0, item)
                        continue

                    if coluna == 14:  # Comprovante (coluna 14)
                        comprovante = cliente[14]  # Campo "comprovante" está na última posição
                        if comprovante:
                            label = QLabel()
                            pixmap = QPixmap(get_resource_path("icones/check.png")).scaled(20, 20)
                            label.setPixmap(pixmap)
                            label.setAlignment(Qt.AlignCenter)
                            self.tabela_clientes.setCellWidget(linha, 14, label)
                        else:
                            # Limpa o widget caso não haja comprovante
                            self.tabela_clientes.setCellWidget(linha, 14, None)
                            item = QTableWidgetItem("")
                            item.setTextAlignment(Qt.AlignCenter)
                            self.tabela_clientes.setItem(linha, 14, item)
                        continue

                    # Mapeamento ajustado dos índices do banco para a tabela:
                    # Colunas 1-7: índices 1-7 do banco
                    # Colunas 8-13: índices 8-13 do banco (pulando o comprovante)
                    if coluna >= 1 and coluna <= 7:
                        cliente_idx = coluna
                    elif coluna >= 8 and coluna <= 13:
                        cliente_idx = coluna
                    else:
                        cliente_idx = 0  # Valor padrão para evitar erros

                    valor = str(cliente[cliente_idx]) if cliente_idx < len(cliente) else ""

                    # Formatações específicas (telefone, CPF/CNPJ, datas, etc.)
                    if coluna == 2:  # Telefone
                        valor = CadastroClienteDialog.formatar_telefone(valor)
                    elif coluna == 3:  # CPF/CNPJ
                        valor = CadastroClienteDialog.formatar_cpf_cnpj(valor)
                    elif coluna == 14:  # Comprovante (já tratado)
                        continue
                    elif coluna in [6, 7, 8]:  # Último Pagamento, Vencimento, Data Aviso
                        try:
                            valor = datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
                        except Exception:
                            pass
                    elif coluna == 9:  # Avisado
                        valor = "SIM" if valor == "1" else "NÃO"

                    # Definição do item da tabela
                    item = QTableWidgetItem(valor)
                    # Define o alinhamento com base na coluna
                    if coluna in colunas_alinhamento_esquerda:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Alinhamento à esquerda
                    else:
                        item.setTextAlignment(Qt.AlignCenter)  # Centraliza o texto

                    # Cores para Status (coluna 11)
                    if coluna == 10:
                        cor = QColor(173, 216, 230) if valor == 'Expirando' else \
                            QColor(255, 182, 193) if valor == 'Inadimplente' else None
                        if cor:
                            item.setBackground(cor)

                    # Insere o item na tabela (exceto para a coluna de comprovante)
                    if coluna != 14:
                        self.tabela_clientes.setItem(linha, coluna, item)
                    # Garante que a coluna de comprovante sempre mostre o ícone
                    elif coluna == 14 and comprovante:
                        label = QLabel()
                        pixmap = QPixmap("icones/check.png").scaled(20, 20)
                        label.setPixmap(pixmap)
                        label.setAlignment(Qt.AlignCenter)
                        self.tabela_clientes.setCellWidget(linha, 14, label)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, 'Erro', f'Erro ao atualizar tabela: {str(e)}')

    def adicionar_cliente(self):
        dialog = CadastroClienteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_tabela()

    def editar_cliente(self):
        try:
            linha_selecionada = self.tabela_clientes.currentRow()
            if linha_selecionada == -1:
                QMessageBox.warning(self, 'Aviso', 'Selecione um cliente para editar')
                return

            # Verifica se a coluna do ID existe e está preenchida
            if self.tabela_clientes.columnCount() < 1:
                QMessageBox.critical(self, 'Erro', 'Estrutura da tabela incorreta')
                return

            id_item = self.tabela_clientes.item(linha_selecionada, 0)
            if not id_item or not id_item.text().isdigit():
                QMessageBox.critical(self, 'Erro', 'ID do cliente inválido ou não encontrado')
                return

            cliente_id = int(id_item.text())

            # Busca o cliente usando o ID
            cliente = self.database.obter_cliente_por_id(cliente_id)
            if not cliente:
                QMessageBox.warning(self, 'Erro', 'Cliente não encontrado no banco de dados')
                return

            # Abre a janela de edição
            dialog = CadastroClienteDialog(self, cliente)
            if dialog.exec_() == QDialog.Accepted:
                self.atualizar_tabela()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro',
                f'Falha ao editar cliente:\n{str(e)}\nConsulte o console para detalhes.'
            )
            traceback.print_exc()

    def remover_cliente(self):
        linha_selecionada = self.tabela_clientes.currentRow()
        if linha_selecionada >= 0:
            try:
                # Obter o ID REAL da lista de clientes, não da tabela
                clientes = self.database.listar_clientes()

                if linha_selecionada < len(clientes):
                    cliente_id = clientes[linha_selecionada][0]  # ID está na posição 0 da tupla

                    resposta = QMessageBox.question(
                        self, 'Confirmar',
                        'Tem certeza que deseja remover este cliente?',
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if resposta == QMessageBox.Yes:
                        self.database.remover_cliente(cliente_id)
                        self.atualizar_tabela()
                else:
                    QMessageBox.warning(self, 'Erro', 'Índice inválido')

            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao remover cliente: {str(e)}')
                traceback.print_exc()
        else:
            QMessageBox.warning(self, 'Aviso', 'Selecione um cliente para remover')

    def recalcular_status_global(self):
        """Atualiza o status de todos os clientes no banco de dados"""
        db = Database()
        clientes = db.listar_clientes()

        for cliente in clientes:
            cliente_id = cliente[0]
            vencimento = cliente[7]  # Índice do vencimento

            novo_status = calcular_status(vencimento)
            db.atualizar_status_cliente(cliente_id, novo_status)

    def abrir_janela_pesquisa(self):
        try:
            dialog = PesquisaClienteDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                criterio = dialog.criterio.currentText()
                valores = dialog.get_valores_selecionados()
                self.filtrar_tabela(criterio, valores)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro na janela de pesquisa: {str(e)}')
            traceback.print_exc()

    def filtrar_tabela(self, criterio: str, valores: list):
        try:
            if not valores:
                self.atualizar_tabela()
                return

            # Validação especial para datas
            if criterio == 'Vencimento (DD/MM/AAAA)':
                valores = [v for v in valores if v.strip() != '']
                if not valores:
                    self.atualizar_tabela()
                    return

            clientes = self.database.pesquisar_clientes(criterio, valores)
            self.exibir_resultados_pesquisa(clientes)

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro na pesquisa: {str(e)}')
            traceback.print_exc()

    def exibir_resultados_pesquisa(self, clientes):
        self.tabela_clientes.setRowCount(len(clientes))

        # Índices das colunas que devem ter alinhamento à esquerda
        colunas_alinhamento_esquerda = [1, 4, 13]  # Nome, E-mail, Observação

        for linha, cliente in enumerate(clientes):
            # Primeiro, adicione o ID na coluna 0 (mesmo que esteja oculta)
            id_item = QTableWidgetItem(str(cliente[0]))
            self.tabela_clientes.setItem(linha, 0, id_item)

            # Processa cada coluna
            for coluna in range(15):  # Itera todas as 15 colunas
                if coluna == 0:  # ID (já tratado)
                    continue

                if coluna == 14:  # Comprovante (coluna 14)
                    comprovante = cliente[14]  # Campo "comprovante" está na última posição
                    if comprovante:
                        label = QLabel()
                        pixmap = QPixmap("icones/check.png").scaled(20, 20)
                        label.setPixmap(pixmap)
                        label.setAlignment(Qt.AlignCenter)
                        self.tabela_clientes.setCellWidget(linha, 14, label)
                    else:
                        # Limpa o widget caso não haja comprovante
                        self.tabela_clientes.setCellWidget(linha, 14, None)
                        item = QTableWidgetItem("")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabela_clientes.setItem(linha, 14, item)
                    continue

                # Para as outras colunas
                cliente_idx = coluna
                valor = str(cliente[cliente_idx]) if cliente_idx < len(cliente) else ""

                # Formatações específicas
                if coluna == 2:  # Telefone
                    valor = CadastroClienteDialog.formatar_telefone(valor)
                elif coluna == 3:  # CPF/CNPJ
                    valor = CadastroClienteDialog.formatar_cpf_cnpj(valor)
                elif coluna in [6, 7, 8]:  # Último Pagamento, Vencimento, Data Aviso
                    try:
                        valor = datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except Exception:
                        pass
                elif coluna == 9:  # Avisado
                    valor = "SIM" if valor == "1" else "NÃO"

                # Cria e configura o item da tabela
                item = QTableWidgetItem(valor)
                if coluna in colunas_alinhamento_esquerda:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)

                # Cores para Status (coluna 10)
                if coluna == 10:
                    cor = QColor(173, 216, 230) if valor == 'Expirando' else \
                        QColor(255, 182, 193) if valor == 'Inadimplente' else None
                    if cor:
                        item.setBackground(cor)

                self.tabela_clientes.setItem(linha, coluna, item)
        self.tabela_clientes.setRowCount(len(clientes))

        # Índices das colunas de data
        COLUNA_STATUS = 9  # Índice da coluna de status
        colunas_datas = [5, 6]  # Último Pagamento e Vencimento

        for linha, cliente in enumerate(clientes):
            # Primeiro, adicione o ID na coluna 0 (mesmo que esteja oculta)
            id_item = QTableWidgetItem(str(cliente[0]))
            self.tabela_clientes.setItem(linha, 0, id_item)

            # Depois, adicione os demais dados a partir da coluna 1
            for coluna, valor in enumerate(cliente[1:], 1):  # Começa do índice 1
                item = QTableWidgetItem(str(valor if valor is not None else ""))

                # Converter datas para formato BR
                if coluna - 1 in colunas_datas:  # -1 porque agora estamos começando do índice 1
                    try:
                        data_iso = datetime.strptime(str(valor), "%Y-%m-%d")
                        item.setText(data_iso.strftime("%d/%m/%Y"))
                    except (ValueError, TypeError):
                        pass

                # Define o alinhamento com base na coluna
                if coluna in colunas_alinhamento_esquerda:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Alinhamento à esquerda
                else:
                    item.setTextAlignment(Qt.AlignCenter)  # Centraliza o texto

                # Aplicar cores baseadas no status
                if coluna - 1 == COLUNA_STATUS:  # -1 pela mesma razão
                    if valor == "Expirando":
                        item.setBackground(QColor(173, 216, 230))  # Azul claro
                    elif valor == "Inadimplente":
                        item.setBackground(QColor(255, 182, 193))  # Vermelho claro
                    item.setForeground(QColor(0, 0, 0))  # Texto preto para contraste

                self.tabela_clientes.setItem(linha, coluna, item)

    def abrir_renovacao(self):
        linha_selecionada = self.tabela_clientes.currentRow()
        if linha_selecionada >= 0:
            clientes = self.database.listar_clientes()
            if 0 <= linha_selecionada < len(clientes):
                cliente = clientes[linha_selecionada]
                dialog = RenovacaoDialog(self, cliente)
                if dialog.exec_() == QDialog.Accepted:
                    self.atualizar_tabela()

    def ver_comprovante(self):
        try:
            linha_selecionada = self.tabela_clientes.currentRow()
            if linha_selecionada == -1:
                QMessageBox.warning(self, 'Aviso', 'Selecione um cliente para visualizar o comprovante.')
                return

            # Obtém o ID do cliente selecionado
            id_item = self.tabela_clientes.item(linha_selecionada, 0)
            if not id_item or not id_item.text().isdigit():
                QMessageBox.critical(self, 'Erro', 'ID do cliente inválido ou não encontrado.')
                return

            cliente_id = int(id_item.text())

            # Busca o cliente no banco de dados
            cliente = self.database.obter_cliente_por_id(cliente_id)
            if not cliente:
                QMessageBox.warning(self, 'Erro', 'Cliente não encontrado no banco de dados.')
                return

            # Verifica se há um comprovante associado
            comprovante_hash = cliente.get('comprovante', None)
            if not comprovante_hash:
                QMessageBox.information(self, 'Informação', 'Nenhum comprovante encontrado para este cliente.')
                return

            # Monta o caminho completo do comprovante
            comprovante_path = os.path.join(COMPROVANTES_DIR, comprovante_hash)
            if not os.path.exists(comprovante_path):
                QMessageBox.warning(self, 'Erro', 'Arquivo do comprovante não encontrado.')
                return

            # Abre a janela de visualização do comprovante
            dialog = ComprovanteDialog(comprovante_path, self)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao visualizar comprovante: {str(e)}')
            traceback.print_exc()

    def abrir_janela_relatorio(self):
        dialog = RelatorioDialog(self)
        dialog.exec_()

    def importar_csv(self):
        try:
            # Abre o diálogo para selecionar o arquivo CSV
            arquivo_csv, _ = QFileDialog.getOpenFileName(
                self,
                'Selecionar arquivo CSV',
                '',
                'Arquivos CSV (*.csv)'
            )

            if arquivo_csv:
                # Tenta importar o arquivo CSV usando o método do banco de dados
                registros_importados, registros_falhos = self.database.importar_csv(arquivo_csv)

                # Exibe mensagem com o resultado da importação
                QMessageBox.information(
                    self,
                    'Importação Concluída',
                    f'Importação concluída com sucesso!\n\n'
                    f'Registros importados: {registros_importados}\n'
                    f'Registros com falha: {registros_falhos}'
                )

                # Atualiza a tabela para mostrar os novos registros
                self.atualizar_tabela()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Erro na Importação',
                f'Ocorreu um erro durante a importação:\n{str(e)}'
            )

    def avisar_cliente(self):
        linha_selecionada = self.tabela_clientes.currentRow()
        if linha_selecionada == -1:
            QMessageBox.warning(self, "Aviso", "Selecione um cliente para avisar.")
            return
        id_item = self.tabela_clientes.item(linha_selecionada, 0)
        if not id_item or not id_item.text().isdigit():
            QMessageBox.critical(self, "Erro", "ID do cliente inválido ou não encontrado.")
            return
        cliente_id = int(id_item.text())
        cliente = self.database.obter_cliente_por_id(cliente_id)
        if not cliente:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado.")
            return

        dialog = AvisoClienteDialog(self, cliente)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_tabela()


class CadastroClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.setWindowTitle('Cadastro de Cliente')
        self.database = Database()
        self.cliente = cliente
        self.comprovante_path = None

        layout = QFormLayout()

        self.nome = QLineEdit()

        # Configuração do QLineEdit para Telefone com máscara fixa para celular (11 dígitos)
        self.telefone = QLineEdit()
        self.telefone.setInputMask('(00) 00000-0000;_')
        self.telefone.textChanged.connect(self.atualizarMascaraTelefone)

        # Configuração do QLineEdit para CPF/CNPJ com máscara dinâmica
        self.cpf_cnpj = QLineEdit()
        self.cpf_cnpj.setPlaceholderText("Digite CPF ou CNPJ")
        self.cpf_cnpj.textChanged.connect(self.atualizarMascaraCpfCnpj)

        self.email = QLineEdit()
        self.periodo_assinatura = QLineEdit()

        # Configura último pagamento para hoje por padrão
        self.ultimo_pagamento = QDateEdit()
        self.ultimo_pagamento.setDate(QDate.currentDate())
        self.ultimo_pagamento.setCalendarPopup(True)

        # Torna o campo de vencimento somente leitura
        self.vencimento = QLineEdit()
        self.vencimento.setReadOnly(True)

        # Evento para calcular vencimento quando o período muda
        self.periodo_assinatura.textChanged.connect(self.calcular_vencimento)
        self.ultimo_pagamento.dateChanged.connect(self.calcular_vencimento)

        # Status será exibido apenas na edição
        self.status = None
        if cliente:
            self.status = QComboBox()
            self.status.addItems(['Em dia', 'Expirando', 'Inadimplente'])
            layout.addRow('Status:', self.status)

        self.estado = QComboBox()
        estados_brasileiros = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        self.estado.addItems(estados_brasileiros)

        self.cidade = QLineEdit()
        self.observacao = QLineEdit()

        # Adicionar botão para o comprovante
        botao_comprovante = QPushButton('Carregar Comprovante')
        botao_comprovante.clicked.connect(self.carregar_comprovante)

        layout.addRow('Nome:', self.nome)
        layout.addRow('Telefone:', self.telefone)
        layout.addRow('CPF/CNPJ:', self.cpf_cnpj)
        layout.addRow('E-mail:', self.email)
        layout.addRow('Período Assinatura:', self.periodo_assinatura)
        layout.addRow('Último Pagamento:', self.ultimo_pagamento)
        layout.addRow('Vencimento:', self.vencimento)
        layout.addRow('Estado:', self.estado)
        layout.addRow('Municipio:', self.cidade)
        layout.addRow('Observação:', self.observacao)
        layout.addRow('Comprovante:', botao_comprovante)

        botao_salvar = QPushButton('Salvar')
        botao_salvar.clicked.connect(self.salvar_cliente)
        layout.addRow(botao_salvar)

        self.setLayout(layout)

        # Se for uma edição, preenche os campos
        if cliente:
            try:
                self.preencher_campos(cliente)
            except Exception as e:
                print(f"Erro ao preencher campos: {e}")
                traceback.print_exc()
                QMessageBox.critical(self, 'Erro', f'Erro ao carregar dados do cliente: {e}')
                self.reject()

        # Calcula vencimento inicial
        self.calcular_vencimento()

    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        numeros = ''.join(filter(str.isdigit, telefone))
        if len(numeros) == 11:
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        # Se não tiver 11 dígitos, retorna o formato original
        return telefone

    @staticmethod
    def formatar_cpf_cnpj(valor: str) -> str:
        numeros = ''.join(filter(str.isdigit, valor))
        if len(numeros) == 11:
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) == 14:
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        return valor

    def atualizarMascaraTelefone(self, text):
        # Remove caracteres não numéricos para contar os dígitos
        digits = ''.join(filter(str.isdigit, text))
        
        # Sempre usa a máscara de celular (11 dígitos)
        new_mask = '(00) 00000-0000;_'
        
        if self.telefone.inputMask() != new_mask:
            # Bloqueia sinais para evitar loop
            self.telefone.blockSignals(True)
            cursor_pos = self.telefone.cursorPosition()
            self.telefone.setInputMask(new_mask)
            
            # Limita para exatamente 11 dígitos (celular)
            if len(digits) > 11:
                digits = digits[:11]  # Limita a 11 dígitos
                
            self.telefone.setText(digits)
            
            # Tenta manter a posição do cursor
            if cursor_pos < len(self.telefone.text()):
                self.telefone.setCursorPosition(cursor_pos)
                
            self.telefone.blockSignals(False)

    def atualizarMascaraCpfCnpj(self, text):
        # Remove caracteres não numéricos
        digits = ''.join(filter(str.isdigit, text))

        # Define a máscara com base no comprimento dos dígitos
        if len(digits) <= 11:
            new_mask = '000.000.000-00;_'
        else:
            new_mask = '00.000.000/0000-00;_'

        # Atualiza a máscara apenas se necessário
        if self.cpf_cnpj.inputMask() != new_mask:
            self.cpf_cnpj.blockSignals(True)
            self.cpf_cnpj.setInputMask(new_mask)

            # Mantém os dígitos e preenche com placeholders para a máscara
            if len(digits) > 14:  # Limita para 14 dígitos (CNPJ)
                digits = digits[:14]
            elif len(digits) > 11 and len(digits) < 14:  # Completa com placeholders
                digits = digits.ljust(14, '_')

            self.cpf_cnpj.setText(digits)
            self.cpf_cnpj.blockSignals(False)

    def calcular_vencimento(self):
        try:
            # Obtém a data do último pagamento
            ultimo_pagamento = self.ultimo_pagamento.date().toPyDate()

            # Obtém o período de assinatura
            try:
                periodo = int(self.periodo_assinatura.text() or 1) * 30
            except (ValueError, TypeError):
                periodo = 30

            # Calcula a data de vencimento
            vencimento = ultimo_pagamento + timedelta(days=periodo)

            # Define a data de vencimento no campo
            self.vencimento.setText(vencimento.strftime('%d/%m/%Y'))
        except Exception as e:
            # Se houver erro no cálculo, limpa o campo
            print(f"Erro no cálculo de vencimento: {e}")
            self.vencimento.clear()

    def calcular_status(self, vencimento):
        """
        Calcula o status do cliente baseado na data de vencimento

        Args:
            vencimento (datetime.date): Data de vencimento do cliente

        Returns:
            str: Status do cliente ('Em dia', 'Expirando', 'Inadimplente')
        """
        hoje = datetime.now().date()

        if vencimento > hoje:
            dias_para_vencimento = (vencimento - hoje).days

            if dias_para_vencimento >= 6:
                return 'Em dia'
            else:
                return 'Expirando'
        else:
            return 'Inadimplente'

    def preencher_campos(self, cliente):

        # Se o cliente for um dicionário, use os nomes das chaves
        if isinstance(cliente, dict):
            self.nome.setText(str(cliente.get('nome', '')))
            
            # Tratamento especial para o telefone
            telefone = str(cliente.get('telefone', ''))
            # Extrai apenas os dígitos do telefone
            digits = ''.join(filter(str.isdigit, telefone))
            
            # Sempre usa a máscara de celular (11 dígitos)
            new_mask = '(00) 00000-0000;_'
            self.telefone.blockSignals(True)
            self.telefone.setInputMask(new_mask)
            self.telefone.setText(digits)
            self.telefone.blockSignals(False)
            
            self.cpf_cnpj.setText(str(cliente.get('cpf_cnpj', '')))
            self.email.setText(str(cliente.get('email', '')))

            # Periodo de assinatura
            self.periodo_assinatura.setText(str(cliente.get('periodo_assinatura', '1')))
            self.periodo_assinatura.setReadOnly(True)
            self.periodo_assinatura.setEnabled(False)

            # Ultimo pagamento
            try:
                ultimo_pagamento = datetime.strptime(str(cliente.get('ultimo_pagamento', '')), "%Y-%m-%d").date()
                self.ultimo_pagamento.setDate(QDate(ultimo_pagamento.year, ultimo_pagamento.month, ultimo_pagamento.day))
            except (ValueError, TypeError):
                self.ultimo_pagamento.setDate(QDate.currentDate())
            self.ultimo_pagamento.setEnabled(False)

            # Vencimento
            try:
                vencimento_iso = cliente.get('vencimento', '')
                vencimento_date = datetime.strptime(vencimento_iso, "%Y-%m-%d")
                self.vencimento.setText(vencimento_date.strftime("%d/%m/%Y"))
            except (ValueError, TypeError):
                self.vencimento.setText("")
            self.vencimento.setReadOnly(True)
            self.vencimento.setEnabled(False)

            # Campos editáveis
            self.estado.setCurrentText(str(cliente.get('estado', 'SP')))
            self.cidade.setText(str(cliente.get('cidade', '')))
            self.observacao.setText(str(cliente.get('observacao', '')))



            # Status
            if self.status:
                try:
                    self.status.setCurrentText(str(cliente.get('status', 'Em dia')))
                except Exception:
                    self.status.setCurrentText('Em dia')
                self.status.setEnabled(False)

    def salvar_cliente(self):
        try:
            if not self.nome.text():
                QMessageBox.warning(self, 'Erro', 'Nome é obrigatório')
                return
                
            # Validação para garantir que o telefone tenha exatamente 11 dígitos
            telefone_digits = ''.join(filter(str.isdigit, self.telefone.text()))
            if len(telefone_digits) != 11:
                QMessageBox.warning(self, 'Erro', 'O telefone deve ter exatamente 11 dígitos')
                return

            if not validar_cpf_cnpj(self.cpf_cnpj.text()):
                QMessageBox.warning(self, 'Erro', 'CPF/CNPJ inválido')
                return

            if not validar_email(self.email.text()):
                QMessageBox.warning(self, 'Erro', 'E-mail inválido')
                return

            # Processar comprovante
            comprovante_hash = None
            if self.comprovante_path and os.path.isfile(self.comprovante_path):
                # Verificar e criar diretório se necessário
                os.makedirs(COMPROVANTES_DIR, exist_ok=True)

                # Gerar nome baseado em hash
                hash_name = hashlib.sha256(
                    f"{self.nome.text()}{datetime.now().timestamp()}".encode()
                ).hexdigest()[:16]

                ext = os.path.splitext(self.comprovante_path)[1]
                novo_nome = f"{hash_name}{ext}"
                destino = os.path.join(COMPROVANTES_DIR, novo_nome)

                # Copiar arquivo para o diretório de comprovantes
                shutil.copy(self.comprovante_path, destino)
                comprovante_hash = novo_nome

            if self.cliente:  # Edição
                cliente_completo = (
                    self.nome.text(),
                    self.telefone.text(),
                    self.cpf_cnpj.text(),
                    self.email.text(),
                    int(self.cliente.get('periodo_assinatura', 1)),  # Acessa como dicionário
                    self.cliente.get('ultimo_pagamento', QDate.currentDate().toString("yyyy-MM-dd")),
                    self.cliente.get('vencimento', ''),
                    None,
                    0,
                    self.cliente.get('status', 'Em dia'),
                    self.estado.currentText(),
                    self.cidade.text(),
                    self.observacao.text(),
                    comprovante_hash if comprovante_hash else self.cliente.get('comprovante', ''),  # Manter comprovante se não for alterado
                    self.cliente['id']  # ID do dicionário
                )
                self.database.atualizar_cliente(cliente_completo)
            else:  # Novo cliente
                vencimento_date = datetime.strptime(self.vencimento.text(), "%d/%m/%Y")
                cliente = (
                    self.nome.text(),
                    self.telefone.text(),
                    self.cpf_cnpj.text(),
                    self.email.text(),
                    int(self.periodo_assinatura.text()),
                    self.ultimo_pagamento.date().toString("yyyy-MM-dd"),
                    vencimento_date.strftime("%Y-%m-%d"),
                    None,
                    0,
                    self.calcular_status(vencimento_date.date()),
                    self.estado.currentText(),
                    self.cidade.text(),
                    self.observacao.text(),
                    comprovante_hash  # Adicionar o hash do comprovante
                )
                self.database.adicionar_cliente(cliente)

            self.accept()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, 'Erro', f'Erro ao salvar cliente: {str(e)}')

    def carregar_comprovante(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Selecionar Comprovante", "",
                "Imagens (*.jpg *.jpeg *.png *.bmp)", options=options
            )
            if file_name:
                if os.path.exists(file_name):
                    self.comprovante_path = file_name
                else:
                    QMessageBox.warning(self, 'Aviso', 'Arquivo selecionado não existe.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao carregar arquivo: {str(e)}')
            import traceback
            traceback.print_exc()

class PesquisaClienteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Pesquisar Clientes')
        self.setFixedSize(400, 300)  # Tamanho ajustado

        layout = QVBoxLayout()

        # Campo de critério
        self.criterio = QComboBox()
        self.criterio.addItems([
            'Nome',
            'Telefone',
            'CPF/CNPJ',
            'E-mail',
            'Vencimento (DD/MM/AAAA)',
            'Status',
            'Estado'
        ])
        self.criterio.currentTextChanged.connect(self.atualizar_campo_valor)

        # Componentes de entrada
        self.campo_texto = QLineEdit()
        self.campo_texto.setPlaceholderText("Digite o valor...")

        self.lista_status = QListWidget()
        self.lista_status.addItems(['Em dia', 'Expirando', 'Inadimplente'])
        self.lista_status.setSelectionMode(QListWidget.MultiSelection)

        self.lista_estados = QListWidget()
        estados = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        self.lista_estados.addItems(estados)
        self.lista_estados.setSelectionMode(QListWidget.MultiSelection)

        # Container para os componentes
        self.container = QWidget()
        self.layout_container = QVBoxLayout()
        self.layout_container.addWidget(self.campo_texto)
        self.layout_container.addWidget(self.lista_status)
        self.layout_container.addWidget(self.lista_estados)
        self.container.setLayout(self.layout_container)

        # Botões
        botao_pesquisar = QPushButton('Pesquisar')
        botao_pesquisar.clicked.connect(self.accept)
        botao_cancelar = QPushButton('Cancelar')
        botao_cancelar.clicked.connect(self.reject)

        # Layout principal
        layout.addWidget(QLabel('Critério:'))
        layout.addWidget(self.criterio)
        layout.addWidget(QLabel('Valor:'))
        layout.addWidget(self.container)
        layout.addWidget(botao_pesquisar)
        layout.addWidget(botao_cancelar)

        self.setLayout(layout)
        self.atualizar_campo_valor()

    def atualizar_campo_valor(self):
        criterio = self.criterio.currentText()

        # Oculta todos os componentes
        self.campo_texto.hide()
        self.lista_status.hide()
        self.lista_estados.hide()

        # Mostra o componente correto
        if criterio in ['Nome', 'Telefone', 'CPF/CNPJ', 'E-mail', 'Vencimento (DD/MM/AAAA)']:
            self.campo_texto.show()
            self.campo_texto.clear()
        elif criterio == 'Status':
            self.lista_status.show()
        elif criterio == 'Estado':
            self.lista_estados.show()

    def get_valores_selecionados(self):
        criterio = self.criterio.currentText()
        if criterio in ['Status', 'Estado']:
            if criterio == 'Status':
                return [item.text() for item in self.lista_status.selectedItems()]
            else:
                return [item.text() for item in self.lista_estados.selectedItems()]
        else:
            return [self.campo_texto.text().strip()]

class RenovacaoDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.setWindowTitle('Renovar Assinatura')
        self.cliente = cliente
        self.database = Database()
        self.comprovante_path = None

        layout = QVBoxLayout()

        # Campos editáveis
        self.periodo_assinatura = QLineEdit(str(cliente[5]))
        self.ultimo_pagamento = QDateEdit()
        self.ultimo_pagamento.setDate(QDate.currentDate())
        self.ultimo_pagamento.setCalendarPopup(True)

        # Botão de upload
        btn_upload = QPushButton('Carregar Comprovante')
        btn_upload.clicked.connect(self.carregar_comprovante)

        # Botão de salvar
        btn_salvar = QPushButton('Salvar Renovação')
        btn_salvar.clicked.connect(self.salvar_renovacao)

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow('Novo Período (meses):', self.periodo_assinatura)
        form_layout.addRow('Novo Último Pagamento:', self.ultimo_pagamento)

        layout.addLayout(form_layout)
        layout.addWidget(btn_upload)
        layout.addWidget(btn_salvar)

        self.setLayout(layout)
        self.calcular_novo_vencimento()

        # Conecta sinais para cálculo automático
        self.periodo_assinatura.textChanged.connect(self.calcular_novo_vencimento)
        self.ultimo_pagamento.dateChanged.connect(self.calcular_novo_vencimento)

    def carregar_comprovante(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Selecionar Comprovante", "",
                "Imagens (*.jpg *.jpeg *.png *.bmp)", options=options
            )
            if file_name:
                if os.path.exists(file_name):
                    self.comprovante_path = file_name
                else:
                    QMessageBox.warning(self, 'Aviso', 'Arquivo selecionado não existe.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao carregar arquivo: {str(e)}')
            traceback.print_exc()

    def calcular_novo_vencimento(self):
        try:
            periodo = int(self.periodo_assinatura.text()) * 30
            ultimo_pagamento = self.ultimo_pagamento.date().toPyDate()
            novo_vencimento = ultimo_pagamento + timedelta(days=periodo)
            self.novo_vencimento = novo_vencimento.strftime('%Y-%m-%d')
            self.novo_status = calcular_status(novo_vencimento)
        except:
            self.novo_vencimento = "Erro no cálculo"
            self.novo_status = "Erro"

    def salvar_renovacao(self):
        try:
            # Verificar e criar diretório se necessário
            os.makedirs(COMPROVANTES_DIR, exist_ok=True)

            # Processar comprovante
            comprovante_hash = None
            if self.comprovante_path and os.path.isfile(self.comprovante_path):
                hash_name = hashlib.sha256(
                    f"{self.cliente[0]}{datetime.now().timestamp()}".encode()
                ).hexdigest()[:16]

                ext = os.path.splitext(self.comprovante_path)[1]
                novo_nome = f"{hash_name}{ext}"
                destino = os.path.join(COMPROVANTES_DIR, novo_nome)

                # Remover arquivo antigo
                if len(self.cliente) > 14 and self.cliente[14]:
                    old_path = os.path.join(COMPROVANTES_DIR, self.cliente[14])
                    if os.path.exists(old_path):
                        os.remove(old_path)

                shutil.copy(self.comprovante_path, destino)
                comprovante_hash = novo_nome

            # Construir dados atualizados
            cliente_atualizado = (
                self.cliente[1],   # nome
                self.cliente[2],   # telefone
                self.cliente[3],   # cpf_cnpj
                self.cliente[4],   # email
                int(self.periodo_assinatura.text()),
                self.ultimo_pagamento.date().toString('yyyy-MM-dd'),
                self.novo_vencimento,
                self.cliente[8] if len(self.cliente) > 8 else '',
                self.cliente[9] if len(self.cliente) > 9 else 0,
                self.novo_status,
                self.cliente[11] if len(self.cliente) > 11 else '',
                self.cliente[12] if len(self.cliente) > 12 else '',
                self.cliente[13] if len(self.cliente) > 13 else '',
                comprovante_hash,
                self.cliente[0]  # ID
            )

            self.database.atualizar_cliente(cliente_atualizado)
            self.accept()

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, 'Erro', f'Falha na renovação: {str(e)}')

class ComprovanteDialog(QDialog):
    def __init__(self, comprovante_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Comprovante de Pagamento')

        # Cria um layout vertical
        layout = QVBoxLayout()

        # Cria um QLabel para exibir a imagem
        self.label_imagem = QLabel()
        self.label_imagem.setAlignment(Qt.AlignCenter)

        # Adiciona a label a um QScrollArea para que imagens grandes possam ser navegadas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.label_imagem)
        layout.addWidget(self.scroll_area)

        # Botão para fechar a janela
        botao_fechar = QPushButton('Fechar')
        botao_fechar.clicked.connect(self.close)
        layout.addWidget(botao_fechar)

        self.setLayout(layout)

        # Carrega a imagem
        self.carregar_imagem(comprovante_path)

    def carregar_imagem(self, comprovante_path):
        if os.path.exists(comprovante_path):
            pixmap = QPixmap(comprovante_path)
            self.label_imagem.setPixmap(pixmap)

            # Define o tamanho máximo baseado na área disponível da tela (com margem)
            screen_geometry = QApplication.desktop().availableGeometry(self)
            max_width = screen_geometry.width() - 100
            max_height = screen_geometry.height() - 100

            # Calcula as dimensões desejadas, respeitando o tamanho da imagem e os limites da tela
            new_width = min(pixmap.width(), max_width)
            new_height = min(pixmap.height(), max_height)

            self.resize(new_width, new_height)
        else:
            QMessageBox.warning(self, 'Erro', 'Comprovante não encontrado.')

class RelatorioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Relatórios')
        self.setMinimumSize(800, 600)
        self.database = Database()
        self.current_figure = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Botões superiores
        btn_top_layout = QHBoxLayout()
        self.btn_estado = QPushButton('Estado', self)
        self.btn_estado.clicked.connect(self.gerar_relatorio_estado)
        self.btn_municipio = QPushButton('Município', self)
        self.btn_municipio.clicked.connect(self.gerar_relatorio_municipio)

        # Botões de zoom
        zoom_layout = QHBoxLayout()
        self.btn_zoom_in = QPushButton('Zoom +', self)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out = QPushButton('Zoom -', self)
        self.btn_zoom_out.clicked.connect(self.zoom_out)

        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)

        btn_top_layout.addWidget(self.btn_estado)
        btn_top_layout.addWidget(self.btn_municipio)
        btn_top_layout.addLayout(zoom_layout)

        # Área do gráfico
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Botão de exportação
        btn_exportar = QPushButton('Exportar Gráfico', self)
        btn_exportar.setIcon(QIcon.fromTheme('document-save-as'))
        btn_exportar.clicked.connect(self.exportar_grafico)

        layout.addLayout(btn_top_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(btn_exportar, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def exportar_grafico(self):
        if not self.current_figure:
            QMessageBox.warning(self, 'Aviso', 'Gere um gráfico antes de exportar!')
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Gráfico",
            "",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)",
            options=options
        )

        if file_name:
            try:
                self.current_figure.savefig(
                    file_name,
                    format=file_name.split('.')[-1].lower(),
                    bbox_inches='tight',
                    dpi=100  # Volte para DPI padrão
                )
                QMessageBox.information(self, 'Sucesso', f'Gráfico exportado com sucesso!\n{file_name}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Falha ao exportar gráfico:\n{str(e)}')

    def gerar_relatorio_estado(self):
        clientes = self.database.listar_clientes()
        estados = [cliente[11] for cliente in clientes if cliente[11]]

        # Contagem por estado
        contagem = {}
        for estado in estados:
            contagem[estado] = contagem.get(estado, 0) + 1

        self.plot_pie_chart(contagem, 'Distribuição de Clientes por Estado')

    def gerar_relatorio_municipio(self):
        clientes = self.database.listar_clientes()
        municipios = [f"{cliente[12]} ({cliente[11]})" for cliente in clientes if cliente[12]]

        # Contagem por município
        contagem = {}
        for municipio in municipios:
            contagem[municipio] = contagem.get(municipio, 0) + 1

        self.plot_pie_chart(contagem, 'Distribuição de Clientes por Município')

    def plot_pie_chart(self, data, title):
        self.figure.clear()
        # Set a larger figure size and adjust layout
        self.figure.set_size_inches(10, 8)
        ax = self.figure.add_subplot(111)

        labels = list(data.keys())
        sizes = list(data.values())

        # Create custom labels with both percentage and absolute numbers
        total = sum(sizes)
        custom_labels = [f'{label}\n{size} ({size/total*100:.1f}%)' for label, size in zip(labels, sizes)]

        ax.pie(sizes, labels=custom_labels, startangle=90)
        ax.axis('equal')
        # Add padding between title and plot
        ax.set_title(title, pad=20)
        
        # Adjust layout to prevent overlapping
        self.figure.tight_layout()

        self.current_figure = self.figure
        self.canvas.draw()

    def plot_bar_chart(self, data, title):
        # Limpa a figura atual se existir
        if self.current_figure:
            plt.close(self.current_figure)

        # Cria uma nova figura
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(range(len(data)), list(data.values()))

        # Personaliza o gráfico
        ax.set_title(title)
        ax.set_ylabel('Quantidade de Clientes')

        # Ajusta os rótulos do eixo x
        labels = list(data.keys())
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        # Adiciona os valores sobre as barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')

        # Ajusta o layout para evitar cortes nos rótulos
        plt.tight_layout()

        # Atualiza a figura atual
        self.current_figure = fig
        
        # Atualiza o canvas para exibir o gráfico
        self.canvas.draw()

        # Retorna a figura para exibição
        return fig

    def zoom_in(self):
        if self.current_figure:
            current_size = self.figure.get_size_inches()
            self.figure.set_size_inches(current_size[0] * 1.2, current_size[1] * 1.2)
            self.canvas.draw()

    def zoom_out(self):
        if self.current_figure:
            current_size = self.figure.get_size_inches()
            self.figure.set_size_inches(current_size[0] / 1.2, current_size[1] / 1.2)
            self.canvas.draw()

class AvisoClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.setWindowTitle("Avisar Cliente")
        self.cliente = cliente
        # Utiliza o mesmo objeto Database do MainWindow
        self.database = parent.database

        layout = QFormLayout()

        # Campo Data Aviso – já preenchido com a data atual
        self.data_aviso = QDateEdit()
        self.data_aviso.setDate(QDate.currentDate())
        self.data_aviso.setCalendarPopup(True)
        layout.addRow("Data Aviso:", self.data_aviso)

        # Checkbox para Avisado
        self.chk_avisado = QCheckBox("Avisado")
        self.chk_avisado.setChecked(True)  # Set to True by default
        layout.addRow("Avisado:", self.chk_avisado)

        # Botão WhatsApp (ícone) para enviar mensagem
        self.btn_whatsapp = QPushButton()
        self.btn_whatsapp.setIcon(QIcon(get_resource_path('icones/whatsapp.png')))
        self.btn_whatsapp.setIconSize(QSize(24, 24))
        self.btn_whatsapp.clicked.connect(self.enviar_whatsapp)

        # Botão Limpar para resetar os campos
        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.clicked.connect(self.limpar_campos)

        # Botões de ação: Salvar e Cancelar
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.clicked.connect(self.salvar_aviso)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        # Layout horizontal para os botões
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_whatsapp)
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_cancelar)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def limpar_campos(self):
        # Limpa a data (define como null no banco)
        self.data_aviso.setDate(QDate())
        # Desmarca o checkbox
        self.chk_avisado.setChecked(False)
        # Salva as alterações no banco
        cliente_id = self.cliente['id'] if isinstance(self.cliente, dict) else self.cliente[0]
        self.database.atualizar_aviso_cliente(cliente_id, None, 0)
        # Fecha a janela
        self.accept()

    def salvar_aviso(self):
        # Recupera a data em formato 'yyyy-MM-dd'
        data_aviso_str = self.data_aviso.date().toString("yyyy-MM-dd") if self.data_aviso.date().isValid() else None
        # Define o valor do campo Avisado: 1 para SIM se estiver marcado, senão 0
        avisado_valor = 1 if self.chk_avisado.isChecked() else 0

        # Obtém o ID do cliente (considerando que no BD o cliente pode ser um dicionário ou tupla)
        cliente_id = self.cliente['id'] if isinstance(self.cliente, dict) else self.cliente[0]

        # Chama um método do banco de dados para atualizar os campos "data_aviso" e "avisado"
        self.database.atualizar_aviso_cliente(cliente_id, data_aviso_str, avisado_valor)

        self.accept()

    def enviar_whatsapp(self):
        # Recupera o telefone do cliente – adapte conforme sua estrutura de dados
        telefone = self.cliente['telefone'] if isinstance(self.cliente, dict) else self.cliente[2]
        enviar_mensagem_whatsapp(telefone)

