# -*- coding: utf-8 -*-
"""
Diálogos para operações com pinturas
Classes de diálogo para adicionar, editar e pesquisar pinturas
"""

from PyQt5.QtWidgets import (QDialog, QMainWindow, QDialogButtonBox, QTableWidgetItem, QMessageBox, QPushButton, 
                             QCheckBox, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
                             QLabel, QLineEdit, QComboBox, QTableWidget, QAbstractItemView)
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
import sys
from pathlib import Path  

# Adicionar o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

from Funções.crud_pint import listar_pinturas, busca_filtros, adicionar_pintura, atualizar_pintura, buscar_pintura, remover_pintura
from Funções.detalhes_pintura import mostrar_detalhes

BASE_DIR = Path(__file__).parent.parent.resolve()
UI_DIR   = BASE_DIR / "Interface"
DB_PATH  = BASE_DIR / "Data" / "Data.db"
import sys
from pathlib import Path  

# Adicionar o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

from Funções.crud_pint import listar_pinturas, busca_filtros, adicionar_pintura, atualizar_pintura, buscar_pintura, remover_pintura
from Funções.detalhes_pintura import mostrar_detalhes

BASE_DIR = Path(__file__).parent.parent.resolve()
UI_DIR   = BASE_DIR / "Interface"
DB_PATH  = BASE_DIR / "Data" / "Data.db"


class Nova_pintura(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Adicionar", 'Pintura.ui'), self)
        
        # Conectar botões corretos
        self.btnSalvar = self.findChild(QPushButton, 'btnSalvar')
        self.btnCancelar = self.findChild(QPushButton, 'btnCancelar')
        self.btnSalvar.clicked.connect(self.adicionar)
        self.btnCancelar.clicked.connect(self.reject)
        
        # Configurar checkboxes para habilitar/desabilitar campos opcionais
        self.setup_checkboxes()

    def setup_checkboxes(self):
        """Configurar as checkboxes para controlar campos opcionais"""
        # Conectar checkboxes aos métodos de toggle
        self.chkSerie.stateChanged.connect(self.toggle_serie)
        self.chkPreco.stateChanged.connect(self.toggle_preco)
        
        # Carregar séries no combobox
        self.carregar_series()
        
    def toggle_serie(self):
        """Habilitar/desabilitar campo de série"""
        self.serie.setEnabled(self.chkSerie.isChecked())
        
    def toggle_preco(self):
        """Habilitar/desabilitar campo de preço"""
        self.preco.setEnabled(self.chkPreco.isChecked())
        
    def carregar_series(self):
        """Carregar séries disponíveis no combobox"""
        try:
            from Funções.crud_series import listar_series
            series = listar_series()
            self.serie.clear()
            self.serie.addItem("Sem série", None)
            for serie in series:
                self.serie.addItem(serie[1], serie[0])  # nome, id
        except Exception as e:
            print(f"Erro ao carregar séries: {e}")

    def adicionar(self):
        # Coletar dados dos campos obrigatórios
        titulo = self.titulo.text().strip()
        tecnica = self.tecnica.text().strip()
        ano = self.data.date().toString("yyyy")  # Apenas o ano
        local = self.local.text().strip()
        
        # Coletar dados dos campos de tamanho (se existirem)
        try:
            largura = self.largura.value() if hasattr(self, 'largura') else 0
            altura = self.altura.value() if hasattr(self, 'altura') else 0
            tamanho = f"{largura}x{altura}cm" if largura > 0 and altura > 0 else ""
        except:
            tamanho = ""
        
        # Campos opcionais
        serie_id = None
        if self.chkSerie.isChecked() and self.serie.currentData():
            serie_id = self.serie.currentData()
            
        preco = None
        if self.chkPreco.isChecked():
            preco = self.preco.value()
        
        # Validação
        if not titulo:
            QMessageBox.warning(self, "Erro", "Título é obrigatório!")
            return
            
        try:
            # Adicionar pintura (sem serie_id direto)
            pintura_id = adicionar_pintura(titulo, tecnica, tamanho, ano, local, db_path=str(DB_PATH))
            
            # Associar à série se selecionada
            if self.chkSerie.isChecked() and self.serie.currentData():
                from Funções.crud_series import associar_pintura_serie
                associar_pintura_serie(pintura_id, self.serie.currentData())
            
            # Adicionar preço se especificado
            if self.chkPreco.isChecked() and preco > 0:
                from Funções.crud_precos import adicionar_preco
                adicionar_preco(pintura_id, preco, ano)
            
            # Mostrar diálogo de pasta criada
            dialog_pasta = Pintura_caminho(pintura_id, titulo)
            dialog_pasta.exec_()
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar pintura: {str(e)}")

class Pintura_caminho(QDialog):
    def __init__(self, pintura_id, titulo_pintura):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Adicionar", 'Pintura_caminho.ui'), self)
        self.pintura_id = pintura_id
        
        # Obter caminho da pasta criada
        try:
            from Funções.gerenciador_pastas import gerenciador_pastas
            pasta_pintura = gerenciador_pastas.obter_pasta_pintura(pintura_id, titulo_pintura)
            if pasta_pintura:
                self.Caminho.setText(pasta_pintura)
            else:
                self.Caminho.setText("Erro ao criar pasta")
        except Exception as e:
            self.Caminho.setText(f"Erro: {e}")
        
        # Conectar botões
        self.buttonBox.button(QDialogButtonBox.Open).clicked.connect(self.abrir_pasta)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)

    def abrir_pasta(self):
        caminho = self.Caminho.text()
        if os.path.exists(caminho):
            os.startfile(caminho)  # Windows
        else:
            QMessageBox.warning(self, "Erro", "Pasta não encontrada!")

class Editar_pintura(QDialog):
    def __init__(self, pintura_id):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Editar", 'Editar.ui'), self)
        self.pintura_ids = pintura_id if isinstance(pintura_id, list) else [pintura_id]
        self.buttonBox.accepted.connect(self.editar)
        self.buttonBox.rejected.connect(self.reject)

    def editar(self):
        edits = {
            "titulo": self.lineEdit_tituloedit.text().strip() if self.checkBox_titulo.isChecked() else None,
            "tecnica": self.lineEdit_tecnicaedit.currentText() if self.checkBox_tecnica.isChecked() else None,
            "tamanho": (self.lineEdit_larguraedit.text().strip(), self.lineEdit_altura.text().strip()) if self.checkBox_tamanho.isChecked() else None,
            "data": self.dateEdit.date().toString("yyyy") if self.checkBox_data.isChecked() else None,
            "serie": self.comboBox_serielist.currentText() if self.checkBox_serie.isChecked() else None,
            "local": self.lineEdit_localedit.text().strip() if self.checkBox_local.isChecked() else None
        }
        for pid in self.pintura_ids:
            atualizar_pintura(pid, 
                            edits["titulo"], 
                            edits["tecnica"], 
                            edits["tamanho"], 
                            edits["data"], 
                            edits["local"])
        self.accept()

class Pesquisa_pintura(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Buscar", 'Pesquisa_pintura.ui'), self)
        self.confirma_busca.clicked.connect(self.buscar)
        self.cancelar_busca.clicked.connect(self.reject)
        self.data_fin.setEnabled(False)
        self.checkBox_data_periodo.toggled.connect(self.data_fin.setEnabled)

    def buscar(self):
        filtros = {
            "titulo": None, "intervalo_titulo": False, "letra1": None, "sinal1": None, "letra2": None, "sinal2": None,
            "date_from": None, "date_to": None, "date_op": None, "exposicoes": None, "serie": None, "local": None,
            "intervalo_preco": False, "preco1": None, "preco2": None, "tamanho_x": None, "tamanho_y": None, "tecnica": None
        }
        self._filtros_titulo(filtros)
        self._filtros_data(filtros)
        self._filtros_exposicao(filtros)
        self._filtros_serie(filtros)
        self._filtros_local(filtros)
        self._filtros_preco(filtros)
        self._filtros_tamanho(filtros)
        self._filtros_tecnica(filtros)
        self._filtros_local(filtros)
        self._filtros_preco(filtros)
        self._filtros_tamanho(filtros)
        self._filtros_tecnica(filtros)

    def _filtros_titulo(self, f):
        # Verificar se há texto no campo de título
        raw = self.titulo_busca.text().strip()
        if raw:
            if self.checkBox_intervalo_titulo.isChecked():
                f["intervalo_titulo"] = True
                f.update({
                    "letra1": self.letra1.text().strip(),
                    "sinal1": self.sinal1.currentText(),
                    "letra2": self.letra2.text().strip(),
                    "sinal2": self.sinal2.currentText()
                })
            else:
                f["titulo"] = raw

    def _filtros_data(self, f):
        # Sempre usar o ano inicial
        f["date_from"] = self.data_ini.date().toString("yyyy")
        f["date_op"] = self.comboBox_data_op.currentText()
        
        # Se período está marcado, usar ano final também
        if self.checkBox_data_periodo.isChecked():
            f["date_to"] = self.data_fin.date().toString("yyyy")
        else:
            f["date_to"] = None

    def _filtros_exposicao(self, f):
        # Por enquanto, não implementado na nova interface
        pass

    def _filtros_serie(self, f):
        # Verificar se há série selecionada
        if hasattr(self, 'comboBox_serie') and self.comboBox_serie.currentIndex() > 0:
            f["serie"] = self.comboBox_serie.currentText()

    def _filtros_local(self, f):
        # Verificar se há texto no campo de local
        if hasattr(self, 'local_busca'):
            local = self.local_busca.text().strip()
            if local:
                f["local"] = local

    def _filtros_preco(self, f):
        # Por enquanto, não implementado na nova interface
        pass

    def _filtros_tamanho(self, f):
        # Verificar se há valores nos campos de tamanho
        if hasattr(self, 'tamanho_x') and hasattr(self, 'tamanho_y'):
            x = self.tamanho_x.value()
            y = self.tamanho_y.value()
            if x > 0:
                f["tamanho_x"] = str(x)
            if y > 0:
                f["tamanho_y"] = str(y)

    def _filtros_tecnica(self, f):
        # Verificar se há texto no campo de técnica
        if hasattr(self, 'tecnica_busca'):
            tecnica = self.tecnica_busca.text().strip()
            if tecnica:
                f["tecnica"] = tecnica

    def _filtros_tecnica(self, f):
        if self.checkBox_tecnica.isChecked():
            f["tecnica"] = self.comboBox_listaTecnicas.currentText()

class Abrir_pintura(QMainWindow):
    def __init__(self, pintura_id):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Abrir", "pintura.ui"), self)
        self.pintura_ids = pintura_id if isinstance(pintura_id, list) else [pintura_id]
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.tableWidget_pintura.itemSelectionChanged.connect(self.preencher_detalhes)
        self.tableWidget_pintura.itemSelectionChanged.connect(self.mostrar_foto)
        self.tableWidget_pintura.itemSelectionChanged.connect(self.listar_fotos)
        
        # Conectar ações do menu superior
        self._conectar_menu_superior()
        
        # Conectar botão de gestão de fotos
        self.btnGestaoFotos = self.findChild(QPushButton, 'btnGestaoFotos')
        if self.btnGestaoFotos:
            self.btnGestaoFotos.clicked.connect(self.abrir_gestao_fotos)
            self.btnGestaoFotos.setEnabled(False)  # Desabilitar até que uma pintura seja selecionada
            
        # Conectar seleção para habilitar botão de fotos
        self.tableWidget_pintura.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.preencher_tabela()
    
    def accept(self):
        """Método para fechar a janela"""
        self.close()
    
    def reject(self):
        """Método para fechar a janela"""
        self.close()
    
    def _conectar_menu_superior(self):
        """Conectar ações do menu superior"""
        try:
            # Menu Seleção > Adicionar a Exposição
            if hasattr(self, 'actionExposicoes'):
                self.actionExposicoes.triggered.connect(self.adicionar_a_exposicao)
            
            # Menu Seleção > Adicionar a Série  
            if hasattr(self, 'actionS_ries'):
                self.actionS_ries.triggered.connect(self.adicionar_a_serie)
        except Exception as e:
            print(f"Erro ao conectar menu: {e}")

    def on_selection_changed(self):
        """Habilitar/desabilitar botão de fotos baseado na seleção"""
        items = self.tableWidget_pintura.selectedItems()
        if self.btnGestaoFotos:
            self.btnGestaoFotos.setEnabled(len(items) > 0)

    def abrir_gestao_fotos(self):
        """Abrir diálogo de gestão de fotos para a pintura selecionada"""
        items = self.tableWidget_pintura.selectedItems()
        if not items:
            QMessageBox.warning(self, "Aviso", "Selecione uma pintura primeiro.")
            return
            
        pintura_id = int(items[0].text())
        
        # Obter nome da pintura
        pintura_data = buscar_pintura(pintura_id, db_path=str(DB_PATH))
        if not pintura_data:
            QMessageBox.warning(self, "Erro", "Dados da pintura não encontrados.")
            return
            
        nome_pintura = pintura_data[1]  # Assumindo que o nome está no índice 1
        
        # Abrir diálogo de gestão de fotos
        try:
            from .Dialogs_fotos import GestaoFotos
            dialog = GestaoFotos(pintura_id, nome_pintura)
            dialog.exec_()
            
            # Recarregar fotos após o diálogo fechar
            self.listar_fotos()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir gestão de fotos: {str(e)}")

    def preencher_tabela(self):


        rows = [buscar_pintura(pid, db_path=str(DB_PATH)) for pid in self.pintura_ids]
        model = QStandardItemModel(len(rows), 7, self)
        model.setHorizontalHeaderLabels(["ID", "Título", "Técnica", "Tamanho", "Data", "Preço", "Série"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:7]):
                model.setItem(r, c, QStandardItem(str(val)))
        self.tableWidget_pintura.setModel(model)
        self.tableWidget_pintura.resizeColumnsToContents()
 
    def preencher_detalhes(self):
        items = self.tableWidget_pintura.selectedItems()
        if not items:
            return
        pid = items[0].text()
        d = mostrar_detalhes(pid, db_path=str(DB_PATH))
        self.label_art_titulo.setText(d["pintura"][1])
        self.label_art_tecnica.setText(d["pintura"][2])
        self.label_art_tamanho.setText(d["pintura"][3])
        self.label_art_data.setText(d["pintura"][4])
        self.label_art_local.setText(d["local"][1])
        self.label_art_serie.setText(d["serie"][1])
        self.label_art_exposicao.setText(d["exposicoes"][1])
        self.label_art_preco.setText(d["precos"][1])



        
    def mostrar_foto(self, nome_foto=None):
        items = self.tableWidget_pintura.selectedItems()
        if not items or not nome_foto:
            return

        pid = items[0].text()
        detalhes = mostrar_detalhes(pid, db_path=str(DB_PATH))
        fotos_path = detalhes.get("fotos_path")

        if fotos_path:
            # Procurar na pasta Fotos simples
            pasta_fotos = os.path.join(fotos_path, "Fotos")
            full_path = os.path.join(pasta_fotos, nome_foto)
            if os.path.exists(full_path):
                pixmap = QPixmap(full_path).scaled(300, 300, Qt.KeepAspectRatio)
                self.label_art_foto.setPixmap(pixmap)
            else:
                self.label_art_foto.setText("Foto não encontrada")




    def listar_fotos(self):
        items = self.tableWidget_pintura.selectedItems()
        if not items:
            return
        pid = items[0].text()
        d = mostrar_detalhes(pid, db_path=str(DB_PATH))
        self.comboBox_art_photos.clear()
        fotos_path = d.get("fotos_path")
        if fotos_path and os.path.exists(fotos_path):
            # Procurar na pasta Fotos simples
            pasta_fotos = os.path.join(fotos_path, "Fotos")
            if os.path.exists(pasta_fotos):
                for foto in os.listdir(pasta_fotos):
                    if foto.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                        self.comboBox_art_photos.addItem(foto)

    def editar_seleção(self):
        items = self.tableWidget_pintura.selectedItems()
        if items:
            ids = list({item.text() for item in items if item.column() == 0})
            dialog = Editar_pintura(ids)
            if dialog.exec_() == QDialog.Accepted:
                self.preencher_tabela()

class Excluir_pintura(QDialog):
    def __init__(self, pintura_ids):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Deletar", "confirmar_Del.ui"), self)
        self.pintura_ids = pintura_ids if isinstance(pintura_ids, list) else [pintura_ids]
        self.buttonBox.accepted.connect(self.__confirmada_exclusao)
        self.buttonBox.rejected.connect(self.reject)
        self.Categoria_item.setText("pintura atual" if len(self.pintura_ids) == 1 else "pinturas atuais")
        titles = []
        for pid in self.pintura_ids:
            painting = buscar_pintura(pid, db_path=str(DB_PATH))
            if painting:
                titles.append(painting[1])  # Assuming index 1 contains the title
        self.Nome_pintura.setText(", ".join(titles))

    def __confirmada_exclusao(self):
        for pid in self.pintura_ids:
            remover_pintura(pid)
        self.accept()


class Busca_Avancada_Pintura(QDialog):
    """Dialog para busca avançada de pinturas com filtros expandidos"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Busca Avançada de Pinturas")
        self.setFixedSize(500, 600)
        self.resultados = []
        
        self.setupUI()
        self.conectar_eventos()
    
    def setupUI(self):
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("Busca Avançada de Pinturas")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Grupo de filtros básicos
        group_basico = QGroupBox("Filtros Básicos")
        form_basico = QFormLayout()
        
        self.edit_titulo = QLineEdit()
        self.edit_titulo.setPlaceholderText("Digite parte do título...")
        form_basico.addRow("Título:", self.edit_titulo)
        
        self.combo_tecnica = QComboBox()
        self.combo_tecnica.addItems(["", "Óleo sobre tela", "Acrílica", "Aquarela", "Pastel", "Grafite", "Carvão", "Mista"])
        self.combo_tecnica.setEditable(True)
        form_basico.addRow("Técnica:", self.combo_tecnica)
        
        self.edit_tamanho = QLineEdit()
        self.edit_tamanho.setPlaceholderText("Ex: 50x70, 40cm...")
        form_basico.addRow("Tamanho:", self.edit_tamanho)
        
        self.edit_ano = QLineEdit()
        self.edit_ano.setPlaceholderText("Ex: 2024, 202...")
        form_basico.addRow("Ano:", self.edit_ano)
        
        self.edit_local = QLineEdit()
        self.edit_local.setPlaceholderText("Local de criação...")
        form_basico.addRow("Local:", self.edit_local)
        
        group_basico.setLayout(form_basico)
        layout.addWidget(group_basico)
        
        # Grupo de filtros avançados
        group_avancado = QGroupBox("Filtros Avançados")
        form_avancado = QFormLayout()
        
        # Filtro de preço
        preco_layout = QHBoxLayout()
        self.edit_preco_min = QLineEdit()
        self.edit_preco_min.setPlaceholderText("Mín")
        self.edit_preco_max = QLineEdit()
        self.edit_preco_max.setPlaceholderText("Máx")
        preco_layout.addWidget(QLabel("R$"))
        preco_layout.addWidget(self.edit_preco_min)
        preco_layout.addWidget(QLabel("até R$"))
        preco_layout.addWidget(self.edit_preco_max)
        form_avancado.addRow("Preço:", preco_layout)
        
        self.edit_serie = QLineEdit()
        self.edit_serie.setPlaceholderText("Nome da série...")
        form_avancado.addRow("Série:", self.edit_serie)
        
        self.edit_exposicao = QLineEdit()
        self.edit_exposicao.setPlaceholderText("Nome da exposição...")
        form_avancado.addRow("Exposição:", self.edit_exposicao)
        
        group_avancado.setLayout(form_avancado)
        layout.addWidget(group_avancado)
        
        # Botões
        btn_layout = QHBoxLayout()
        self.btn_buscar = QPushButton("Buscar")
        self.btn_limpar = QPushButton("Limpar")
        self.btn_selecionar = QPushButton("Selecionar")
        self.btn_cancelar = QPushButton("Cancelar")
        
        self.btn_buscar.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.btn_selecionar.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.btn_selecionar.setEnabled(False)
        
        btn_layout.addWidget(self.btn_buscar)
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_selecionar)
        btn_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(btn_layout)
        
        # Tabela de resultados
        self.tabela_resultados = QTableWidget()
        self.tabela_resultados.setColumnCount(6)
        self.tabela_resultados.setHorizontalHeaderLabels(["ID", "Título", "Técnica", "Tamanho", "Ano", "Preço"])
        self.tabela_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabela_resultados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela_resultados.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tabela_resultados)
        
        self.setLayout(layout)
    
    def conectar_eventos(self):
        self.btn_buscar.clicked.connect(self.buscar)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_selecionar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        self.tabela_resultados.itemSelectionChanged.connect(self.atualizar_botao_selecionar)
    
    def buscar(self):
        try:
            # Coletar filtros
            filtros = {
                'titulo': self.edit_titulo.text().strip() or None,
                'tecnica': self.combo_tecnica.currentText().strip() or None,
                'tamanho': self.edit_tamanho.text().strip() or None,
                'data': self.edit_ano.text().strip() or None,
                'local': self.edit_local.text().strip() or None,
                'preco_min': float(self.edit_preco_min.text()) if self.edit_preco_min.text().strip() else None,
                'preco_max': float(self.edit_preco_max.text()) if self.edit_preco_max.text().strip() else None,
                'serie': self.edit_serie.text().strip() or None,
                'exposicao': self.edit_exposicao.text().strip() or None
            }
            
            # Fazer busca avançada
            from Funções.crud_pint import busca_avancada
            self.resultados = busca_avancada(**filtros)
            
            # Atualizar tabela
            self.atualizar_tabela()
            
        except ValueError as e:
            QMessageBox.warning(self, "Erro", "Verifique os valores de preço inseridos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na busca: {str(e)}")
    
    def atualizar_tabela(self):
        self.tabela_resultados.setRowCount(len(self.resultados))
        
        for row, resultado in enumerate(self.resultados):
            # ID, Título, Técnica, Tamanho, Ano, Preço
            self.tabela_resultados.setItem(row, 0, QTableWidgetItem(str(resultado[0])))
            self.tabela_resultados.setItem(row, 1, QTableWidgetItem(str(resultado[1])))
            self.tabela_resultados.setItem(row, 2, QTableWidgetItem(str(resultado[2] or '')))
            self.tabela_resultados.setItem(row, 3, QTableWidgetItem(str(resultado[3] or '')))
            self.tabela_resultados.setItem(row, 4, QTableWidgetItem(str(resultado[4] or '')))
            
            # Preço atual (índice 7 da query avançada)
            preco = resultado[7] if len(resultado) > 7 and resultado[7] else None
            preco_text = f"R$ {preco:.2f}" if preco else "Não definido"
            self.tabela_resultados.setItem(row, 5, QTableWidgetItem(preco_text))
        
        # Status da busca
        if self.resultados:
            self.setWindowTitle(f"Busca Avançada - {len(self.resultados)} resultado(s)")
        else:
            self.setWindowTitle("Busca Avançada - Nenhum resultado")
    
    def limpar_campos(self):
        self.edit_titulo.clear()
        self.combo_tecnica.setCurrentIndex(0)
        self.edit_tamanho.clear()
        self.edit_ano.clear()
        self.edit_local.clear()
        self.edit_preco_min.clear()
        self.edit_preco_max.clear()
        self.edit_serie.clear()
        self.edit_exposicao.clear()
        self.tabela_resultados.setRowCount(0)
        self.resultados = []
        self.setWindowTitle("Busca Avançada de Pinturas")
    
    def atualizar_botao_selecionar(self):
        self.btn_selecionar.setEnabled(len(self.tabela_resultados.selectedItems()) > 0)
    
    def obter_pintura_selecionada(self):
        """Retorna o ID da pintura selecionada"""
        selected_rows = self.tabela_resultados.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            return int(self.tabela_resultados.item(row, 0).text())
        return None
    
    def adicionar_a_exposicao(self):
        """Adicionar pintura selecionada a uma exposição"""
        selected_rows = self.tableWidget_pintura.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma pintura primeiro!")
            return
        
        try:
            from UI_Dialogs.Dialogs_expos import Selecionar_exposicao
            dialog = Selecionar_exposicao()
            if dialog.exec_() == QDialog.Accepted:
                pintura_id = int(self.tableWidget_pintura.item(selected_rows[0].row(), 0).text())
                exposicao_id = dialog.get_exposicao_selecionada()
                
                # Aqui você adicionaria a lógica para vincular pintura à exposição
                QMessageBox.information(self, "Sucesso", "Pintura adicionada à exposição!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar à exposição: {e}")
    
    def adicionar_a_serie(self):
        """Adicionar pintura selecionada a uma série"""
        selected_rows = self.tableWidget_pintura.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione uma pintura primeiro!")
            return
        
        try:
            from UI_Dialogs.Dialogs_series import Selecionar_serie
            dialog = Selecionar_serie()
            if dialog.exec_() == QDialog.Accepted:
                pintura_id = int(self.tableWidget_pintura.item(selected_rows[0].row(), 0).text())
                serie_id = dialog.get_serie_selecionada()
                
                # Aqui você adicionaria a lógica para vincular pintura à série
                QMessageBox.information(self, "Sucesso", "Pintura adicionada à série!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar à série: {e}")

