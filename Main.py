# -*- coding: utf-8 -*-
"""
Gerenciador de Pinturas
Sistema de catalogação e gestão de obras de arte
"""

import sys, os
from pathlib import Path
  
from Funções.detalhes_pintura import mostrar_detalhes
from UI_Dialogs import Dialogs_pintura, Dialogs_univ, Dialogs_expos
from config_dialog import ConfigDialog
from config import config_manager
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon

# Determinar o diretório base correto (funciona tanto no código quanto no executável)
if getattr(sys, 'frozen', False):
    # Se estiver executando como executável (PyInstaller)
    # Para arquivos empacotados, usar o diretório temporário do PyInstaller
    RESOURCE_DIR = Path(sys._MEIPASS)
    # Para dados, usar o diretório onde o executável está (caminho relativo)
    BASE_DIR = Path(".")
else:
    # Se estiver executando como script Python
    BASE_DIR = Path(__file__).parent.resolve()
    RESOURCE_DIR = BASE_DIR

UI_DIR   = RESOURCE_DIR / "Interface"
# Banco de dados usa caminho relativo simples
DB_PATH  = BASE_DIR / "Data" / "Data.db"

from Funções.crud_pint import listar_pinturas, busca_filtros, busca_avancada, adicionar_pintura, atualizar_pintura, buscar_pintura, remover_pintura
from Funções import crud_series




class MainWindow(QMainWindow):
    """
    Janela principal do sistema de gerenciamento de pinturas
    """
    
    def __init__(self):
        """Inicializar interface e conectar eventos"""
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(UI_DIR, 'main', 'interface.ui'), self)
        
        # Configurar interface inicial
        self._configurar_interface()
        self._conectar_eventos()
    
    def _configurar_interface(self):
        """Configurar elementos da interface"""
        # Configurar ícone da janela
        import os
        from PyQt5.QtGui import QIcon
        icone_path = RESOURCE_DIR / 'icon' / 'icone.ico'
        if icone_path.exists():
            self.setWindowIcon(QIcon(str(icone_path)))
        
        # Configurar seleção múltipla nas tabelas
        from PyQt5.QtWidgets import QAbstractItemView
        
        # Permitir seleção múltipla na tabela de pinturas
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Permitir seleção múltipla na tabela de exposições
        self.tableView_3.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Permitir seleção múltipla na tabela de séries
        self.tableView_series.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Carregar dados iniciais
        self.tabelar_pinturas()
        self.tabelar_exposicoes()
        self.tabelar_series()
    
    def _conectar_eventos(self):
        """Conectar todos os eventos da interface"""
        # Conectar ações do menu superior
        self._conectar_menu_superior()
        
        # Eventos da aba Pinturas
        self.pushButton.clicked.connect(self.abrir_busca_avancada)  # Buscar Avançado
        self.pushButton_3.clicked.connect(self.adicionar_pintura)  # +
        self.pushButton_2.clicked.connect(self.abrir_pinturas)  # Abrir
        self.pushButton_4.clicked.connect(self.editar_selecao)  # Editar
        self.pushButton_excluirpintura.clicked.connect(self.excluir_selecao)  # Excluir

        # Eventos da aba Exposições
        self.pushButton_11.clicked.connect(self.abrir_pesquisa_exposicoes)  # Buscar exposições
        self.pushButton_12.clicked.connect(self.adicionar_exposicao)  # + exposições
        self.pushButton_13.clicked.connect(self.abrir_exposicoes)  # Abrir exposições
        self.pushButton_14.clicked.connect(self.editar_exposicao)  # Editar exposições
        self.pushButton_15.clicked.connect(self.excluir_exposicao)  # Excluir exposições
        self.pushButton_adicionarObras.clicked.connect(self.gerenciar_obras_exposicao)  # Gerenciar obras
        # self.tableView_3.selectionModel().selectionChanged.connect(self.on_exposicao_selected)

        # Conectar botões da aba Séries
        self.pushButton_buscarSerie.clicked.connect(self.abrir_pesquisa_series)  # Buscar séries
        self.pushButton_addSerie.clicked.connect(self.add_serie)
        self.pushButton_abrirSerie.clicked.connect(self.abrir_serie)
        self.pushButton_editarSerie.clicked.connect(self.editar_serie)
        self.pushButton_excluirSerie.clicked.connect(self.excluir_serie)

        self.tabelar_pinturas()
        
        # Conectar mudança de aba para carregar dados adequados
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
    
    def _conectar_menu_superior(self):
        """Conectar todas as ações do menu superior"""
        # Menu Pinturas
        self.actionBuscar.triggered.connect(self.abrir_busca_avancada)
        self.actionAbir.triggered.connect(self.abrir_pinturas)  # Note: "Abir" é o nome no .ui
        self.actionAdicionar.triggered.connect(self.adicionar_pintura)
        self.actionEditar.triggered.connect(self.editar_selecao)
        self.actionExcluir.triggered.connect(self.excluir_selecao)
        
        # Menu Exposições
        self.actionNova_Exposi_o.triggered.connect(self.adicionar_exposicao)
        self.actionExposi_es.triggered.connect(self.abrir_exposicoes)
        
        # Menu Séries
        self.actionAdicionar_s_rie.triggered.connect(self.add_serie)
        
        # Menu Arquivo
        self.actionAbrir_Biblioteca.triggered.connect(self.escolher_pasta_biblioteca)
        self.actionConfigura_es.triggered.connect(self.abrir_configuracoes)
    
    
    def abrir_configuracoes(self):
        """Abrir diálogo de configurações"""
        try:
            dialog = ConfigDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir configurações:\n{e}")
    
    def escolher_pasta_biblioteca(self):
        """Atalho rápido para escolher pasta da biblioteca"""
        from PyQt5.QtWidgets import QFileDialog
        
        pasta_atual = config_manager.get_biblioteca_path()
        pasta = QFileDialog.getExistingDirectory(
            self,
            "Escolher Pasta da Biblioteca",
            str(pasta_atual)
        )
        
        if pasta:
            config_manager.set_biblioteca_path(pasta)
            QMessageBox.information(
                self, 
                "Sucesso", 
                f"Pasta da biblioteca alterada para:\n{pasta}\n\nReinicie o aplicativo para aplicar as mudanças."
            )
    
    def mostrar_sobre(self):
        """Mostrar informações sobre o programa"""
        QMessageBox.about(
            self,
            "Sobre o Gerenciador de Pinturas",
            """<h2>Gerenciador de Pinturas v2.0</h2>
            <p>Sistema completo de catalogação e gestão de obras de arte.</p>
            
            <p><b>Funcionalidades:</b></p>
            <ul>
            <li>Gestão de Pinturas, Exposições e Séries</li>
            <li>Busca avançada e filtros</li>
            <li>Organização automática de arquivos</li>
            <li>Gestão visual de fotos</li>
            <li>Sistema de backup e configurações</li>
            </ul>
            
            <p><b>Desenvolvido com:</b> Python, PyQt5, SQLite</p>
            <p><b>Licença:</b> Software Livre</p>
            """
        )
    
    def configurar_colunas_dinamicas(self, table_view):
        """Configurar colunas da tabela de forma dinâmica e responsiva"""
        header = table_view.horizontalHeader()
        
        # ID: tamanho fixo pequeno
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        table_view.setColumnWidth(0, 50)
        
        # Título/Nome: expansível
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Outras colunas: redimensionamento automático pelo conteúdo
        for col in range(2, table_view.model().columnCount() if table_view.model() else 0):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        # Permitir que o usuário redimensione manualmente se desejar
        header.setStretchLastSection(False)

    def on_tab_changed(self, index):
        """Carregar dados da aba selecionada"""
        if index == 0:  # Aba Pinturas
            self.tabelar_pinturas()
        elif index == 1:  # Aba Exposições  
            self.tabelar_exposicoes()
        elif index == 2:  # Aba Séries
            self.tabelar_series()



    def tabelar_pinturas(self):
        rows = listar_pinturas()
        self.preencher_tabela(rows)

    def preencher_tabela(self, rows):
        model = QStandardItemModel(len(rows), 7, self)
        model.setHorizontalHeaderLabels(["ID", "Título", "Técnica", "Tamanho", "Data", "Local", "Série"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:7]):
                model.setItem(r, c, QStandardItem(str(val)))
        self.tableView.setModel(model)
        
        # Configurar tamanho das colunas de forma dinâmica
        self.configurar_colunas_dinamicas(self.tableView)
        
        # Conectar seleção da tabela após preencher
        self.tableView.selectionModel().selectionChanged.connect(self.on_pintura_selected)

    def tabelar_exposicoes(self):
        """Carregar exposições na tabela da aba Exposições"""
        from Funções.crud_exp import listar_exposicoes
        rows = listar_exposicoes()
        self.preencher_tabela_exposicoes(rows)

    def preencher_tabela_exposicoes(self, rows):
        """Preencher a tabela de exposições (tableView_3)"""
        model = QStandardItemModel(len(rows), 8, self)
        model.setHorizontalHeaderLabels(["ID", "Nome", "Tema", "Artistas", "Data", "Local", "Curadoria", "Organizador"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:8]):
                model.setItem(r, c, QStandardItem(str(val)))
        self.tableView_3.setModel(model)
        
        # Configurar tamanho das colunas de forma dinâmica
        self.configurar_colunas_dinamicas(self.tableView_3)
        
        # Conectar seleção da tabela após preencher
        self.tableView_3.selectionModel().selectionChanged.connect(self.on_exposicao_selected)

    def tabelar_series(self):
        """Carregar séries na tabela da aba Séries"""
        series = crud_series.listar_series(db_path=str(DB_PATH))
        self.preencher_tabela_series(series)

    def preencher_tabela_series(self, rows):
        """Preencher a tabela de séries (tableView_series)"""
        model = QStandardItemModel(len(rows), 6, self)
        model.setHorizontalHeaderLabels(["ID", "Nome", "Descrição", "Data Início", "Data Fim", "Nº Pinturas"])
        for r, row in enumerate(rows):
            for c, val in enumerate(row[:6]):
                model.setItem(r, c, QStandardItem(str(val)))
        self.tableView_series.setModel(model)
        
        # Configurar tamanho das colunas de forma dinâmica
        self.configurar_colunas_dinamicas(self.tableView_series)
        
        # Conectar seleção da tabela após preencher
        self.tableView_series.selectionModel().selectionChanged.connect(self.on_serie_selected)

    def abrir_pesquisa(self):
        dialog = Dialogs_pintura.Pesquisa_pintura()
        if dialog.exec_() == QDialog.Accepted:
            filtros = dialog.filtros

            rows = busca_filtros(filtros, db_path=str(DB_PATH))

            self.preencher_tabela(rows)
    
    def abrir_busca_avancada(self):
        """Abrir interface de busca avançada"""
        dialog = Dialogs_pintura.Busca_Avancada_Pintura()
        if dialog.exec_() == QDialog.Accepted:
            pintura_selecionada = dialog.obter_pintura_selecionada()
            if pintura_selecionada:
                # Exibir resultados da busca na tabela principal
                self.preencher_tabela(dialog.resultados)
                
                # Selecionar a pintura específica se foi escolhida
                model = self.tableView.model()
                for row in range(model.rowCount()):
                    if int(model.index(row, 0).data()) == pintura_selecionada:
                        self.tableView.selectRow(row)
                        break

    def adicionar_pintura(self):
        """Abrir dialog para adicionar nova pintura"""
        dialog = Dialogs_pintura.Nova_pintura()
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_pinturas()

    def abrir_pinturas(self):
        """Abrir pinturas selecionadas"""
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            for index in selected:
                row = index.row()
                pintura_id = self.tableView.model().index(row, 0).data()
                dialog = Dialogs_pintura.Pintura_caminho(pintura_id)
                dialog.exec_()

    def editar_selecao(self):
        """Editar pinturas selecionadas"""
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            pintura_ids = [self.tableView.model().index(index.row(), 0).data() for index in selected]
            dialog = Dialogs_pintura.Editar_pintura(pintura_ids)
            if dialog.exec_() == QDialog.Accepted:
                self.carregar_pinturas()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma pintura para editar!")

    def excluir_selecao(self):
        """Excluir pinturas selecionadas"""
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            pintura_ids = [self.tableView.model().index(index.row(), 0).data() for index in selected]
            dialog = Dialogs_pintura.Excluir_pintura(pintura_ids)
            if dialog.exec_() == QDialog.Accepted:
                self.carregar_pinturas()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma pintura para excluir!")

    def adicionar_exposicao(self):
        """Adicionar nova exposição"""
        dialog = Dialogs_expos.Nova_exposicao()
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Sucesso", "Exposição adicionada com sucesso!")
            self.carregar_exposicoes()

    def abrir_exposicoes(self):
        """Abrir diálogo para selecionar e visualizar exposições"""
        # Primeiro, listar exposições disponíveis
        from Funções.crud_exp import listar_exposicoes
        exposicoes = listar_exposicoes()
        
        if not exposicoes:
            QMessageBox.information(self, "Info", "Nenhuma exposição encontrada!")
            return
        
        # Criar diálogo simples para selecionar exposição
        from PyQt5.QtWidgets import QListWidget, QListWidgetItem
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Exposição")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        lista_expos = QListWidget()
        for expo in exposicoes:
            item = QListWidgetItem(f"{expo[0]} - {expo[1]}")  # id - nome
            item.setData(32, expo[0])  # Qt.UserRole = 32
            lista_expos.addItem(item)
        
        layout.addWidget(lista_expos)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        layout.addWidget(buttonBox)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            current_item = lista_expos.currentItem()
            if current_item:
                exposicao_id = current_item.data(32)
                # Abrir diálogo de detalhes da exposição
                expo_dialog = Dialogs_expos.Abrir_exposicao(exposicao_id)
                expo_dialog.exec_()

    def mostrar_detalhes(self, selected, _):
        idx = selected.indexes()
        if not idx: return
        row = idx[0].row()
        pintura_id = int(self.tableView.model().item(row, 0).text())

        # 1) Dados principais da pintura
        from Funções.crud_pint import buscar_pintura
        p = buscar_pintura(pintura_id, db_path=str(DB_PATH))
        # p = (id, titulo, tecnica, tamanho, data, local)

        # 2) Fotos da pintura
        from Funções.crud_fotos import listar_fotos
        fotos = listar_fotos(pintura_id, db_path=str(DB_PATH))

        # 3) Exposições onde a pintura foi exibida
        from Funções.crud_pinturas_exposicoes import listar_exposicoes_pintura
        expos = listar_exposicoes_pintura(pintura_id, db_path=str(DB_PATH))

        # 4) Locais onde a pintura esteve
        from Funções.crud_locais import listar_locais_pintura
        locais = listar_locais_pintura(pintura_id, db_path=str(DB_PATH))

        # 5) Histórico de preços da pintura
        from Funções.crud_precos import listar_precos_pintura
        precos = listar_precos_pintura(pintura_id, db_path=str(DB_PATH))

        # 6) Preço atual da pintura
        from Funções.crud_precos import buscar_preco_atual
        preco_atual = buscar_preco_atual(pintura_id, db_path=str(DB_PATH))

        # 7) Local atual da pintura
        from Funções.crud_locais import buscar_local_atual
        local_atual = buscar_local_atual(pintura_id, db_path=str(DB_PATH))

        # 8) Endereço base das fotos
        from Funções.crud_fotos import get_fotos_path
        try:
            fotos_path = get_fotos_path(db_path=str(DB_PATH))
        except:
            # Se a função não existir, usar caminho padrão
            fotos_path = str(BASE_DIR / "fotos" / str(pintura_id))

        # Agora você tem:
        #   p             → tupla principal (id, titulo, tecnica, tamanho, data, local)
        #   fotos         → lista de (id, caminho, descrição)
        #   expos         → lista de (id, nome, data, local) das exposições
        #   locais        → lista de (id, local, data_entrada, data_saida, observacao, atual)
        #   precos        → lista de (id, preco, data, observacao, ativo)
        #   preco_atual   → (preco, data, observacao) ou None
        #   local_atual   → (local, data_entrada, observacao) ou None
        #   fotos_path    → caminho base para as fotos

        # Índices importantes da pintura:
        # p[0] - id, p[1] - titulo, p[2] - tecnica, p[3] - tamanho, p[4] - data, p[5] - local

        # Para fotos: fotos[i] = (id, caminho, descrição)
        # Para exposições: expos[i] = (id, nome, data, local)
        # Para locais: locais[i] = (id, local, data_entrada, data_saida, observacao, atual)
        # Para preços: precos[i] = (id, preco, data, observacao, ativo)

        # Criar dicionário com todos os detalhes
        detalhes_pintura = {   
            "pintura": p,
            "fotos": fotos,
            "exposicoes": expos,
            "locais": locais,
            "precos": precos,
            "preco_atual": preco_atual,
            "local_atual": local_atual,
            "fotos_path": fotos_path
        }

        # Retornar o dicionário completo
        return detalhes_pintura

    def on_pintura_selected(self):
        """Atualizar detalhes quando uma pintura é selecionada"""
        selected = self.tableView.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            pintura_id = self.tableView.model().index(row, 0).data()
            
            # Buscar detalhes da pintura usando a função global
            detalhes = mostrar_detalhes(pintura_id, db_path=str(DB_PATH))
            
            if detalhes and 'pintura' in detalhes:
                p = detalhes['pintura']
                
                # Informações adicionais (definir ANTES de usar)
                preco_atual = detalhes.get('preco_atual')
                local_atual = detalhes.get('local_atual')
                precos_historico = detalhes.get('precos', [])
                fotos = detalhes.get('fotos', [])
                
                # Atualizar labels da aba Pinturas
                self.label_8.setText(p[1] if len(p) > 1 else '')  # Título
                self.label_15.setText(p[1] if len(p) > 1 else '')  # Título no topo
                self.label_9.setText(p[3] if len(p) > 3 else '')  # Tamanho
                self.label_10.setText(str(p[4]) if len(p) > 4 else '')  # Data
                self.label_11.setText(p[2] if len(p) > 2 else '')  # Técnica
                self.label_12.setText(p[6] if len(p) > 6 and p[6] else 'Sem série')  # Série
                
                # Exposições (apenas exposições)
                exposicoes = detalhes.get('exposicoes', [])
                if exposicoes:
                    exposicoes_info = ", ".join([expo[1] for expo in exposicoes[:3]])
                    if len(exposicoes) > 3:
                        exposicoes_info += f" e mais {len(exposicoes) - 3}"
                else:
                    exposicoes_info = "Nenhuma"
                self.label_13.setText(exposicoes_info)
                
                # Preço
                if preco_atual:
                    preco_text = f"R$ {preco_atual[0]:.2f}"
                    if len(preco_atual) > 1:
                        preco_text += f" (avaliado em {preco_atual[1]})"
                else:
                    preco_text = "Não definido"
                self.label_preco.setText(preco_text)
                
                # Local atual
                if local_atual:
                    local_text = str(local_atual[0])
                    if len(local_atual) > 1:
                        local_text += f" (desde {local_atual[1]})"
                elif p and len(p) > 5:
                    local_text = str(p[5])
                else:
                    local_text = "Não definido"
                self.label_local.setText(local_text)
                
                # Histórico (preços + locais + fotos)
                historico_info = []
                if len(precos_historico) > 1:
                    historico_info.append(f"{len(precos_historico)} avaliações de preço")
                
                locais_historico = detalhes.get('locais', [])
                if len(locais_historico) > 1:
                    historico_info.append(f"{len(locais_historico)} mudanças de local")
                
                if fotos:
                    historico_info.append(f"{len(fotos)} foto(s)")
                else:
                    historico_info.append("Nenhuma foto")
                
                if historico_info:
                    self.label_historico.setText(" • ".join(historico_info))
                else:
                    self.label_historico.setText("Sem histórico")

    def on_exposicao_selected(self):
        """Atualizar detalhes quando uma exposição é selecionada"""
        selected = self.tableView_3.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            exposicao_id = self.tableView_3.model().index(row, 0).data()
            
            # Buscar detalhes da exposição
            from Funções.crud_exp import buscar_exposicao
            try:
                detalhes = buscar_exposicao(exposicao_id, db_path=str(DB_PATH))
                
                if detalhes:
                    # detalhes é uma tupla: (id, nome, tema, artistas, data, local, curadoria, organizador)
                    self.label_42.setText(detalhes[1] if len(detalhes) > 1 else '')  # Título/Nome
                    self.label_33.setText(detalhes[2] if len(detalhes) > 2 else '')  # Tema  
                    self.label_35.setText(str(detalhes[4]) if len(detalhes) > 4 else '')  # Data
                    self.label_39.setText(detalhes[6] if len(detalhes) > 6 else '')  # Curadoria
                    self.label_17.setText(detalhes[5] if len(detalhes) > 5 else '')  # Local
                    self.label_45.setText(detalhes[1] if len(detalhes) > 1 else '')  # Título no topo
                    
                    # Contar número de obras na exposição
                    from Funções.crud_pinturas_exposicoes import contar_obras_exposicao
                    try:
                        num_obras = contar_obras_exposicao(exposicao_id, db_path=str(DB_PATH))
                        self.label_37.setText(str(num_obras))  # Número de obras
                    except Exception as e:
                        print(f"Erro ao contar obras: {e}")
                        self.label_37.setText("0")
                        
            except Exception as e:
                print(f"Erro ao buscar exposição: {e}")
                # Limpar labels em caso de erro
                self.label_42.setText('')
                self.label_33.setText('')
                self.label_35.setText('')
                self.label_39.setText('')
                self.label_17.setText('')
                self.label_45.setText('')
                self.label_37.setText('')

    def abrir_pesquisa_exposicoes(self):
        """Abrir pesquisa para exposições"""
        try:
            from UI_Dialogs.Dialogs_expos import Pesquisa_exposicao
            dialog = Pesquisa_exposicao()
            if dialog.exec_() == QDialog.Accepted:
                # Se o usuário escolheu uma exposição na busca, abrir detalhes
                try:
                    if getattr(dialog, 'selected_exposicao_id', None):
                        expo_id = dialog.selected_exposicao_id
                        expo_dialog = Dialogs_expos.Abrir_exposicao(expo_id)
                        expo_dialog.exec_()
                finally:
                    # Recarregar exposições após busca/visualização
                    self.tabelar_exposicoes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pesquisa de exposições: {str(e)}")
            # Fallback: recarregar todas as exposições
            self.tabelar_exposicoes()

    def abrir_pesquisa_series(self):
        """Abrir pesquisa para séries"""
        try:
            from UI_Dialogs.Dialogs_series import Pesquisa_serie
            dialog = Pesquisa_serie()
            if dialog.exec_() == QDialog.Accepted:
                # Recarregar séries após busca
                self.tabelar_series()

                # Se o diálogo retornou uma série selecionada, localizar a linha e abrir detalhes
                try:
                    serie_id = getattr(dialog, 'selected_serie_id', None)
                    if serie_id:
                        model = self.tableView_series.model()
                        if model:
                            for r in range(model.rowCount()):
                                try:
                                    val = model.index(r, 0).data()
                                except:
                                    val = None
                                if str(val) == str(serie_id):
                                    # Selecionar a linha e abrir detalhe
                                    try:
                                        self.tableView_series.selectRow(r)
                                        self.abrir_serie()
                                    except Exception:
                                        pass
                                    break
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pesquisa de séries: {str(e)}")
            # Fallback: recarregar todas as séries
            self.tabelar_series()

    def add_serie(self):
        """Adicionar nova série"""
        from PyQt5.QtWidgets import QInputDialog, QTextEdit, QSpinBox
        
        nome, ok = QInputDialog.getText(self, 'Nova Série', 'Nome da série:')
        if ok and nome.strip():
            descricao, ok2 = QInputDialog.getMultiLineText(self, 'Nova Série', 'Descrição (opcional):')
            if ok2:
                # Solicitar anos opcionais
                ano_inicio, ok3 = QInputDialog.getInt(self, 'Nova Série', 'Ano de início (opcional):', 
                                                    2000, 1800, 2100, 1)
                if not ok3:
                    ano_inicio = ""
                
                ano_fim = ""
                if ok3:  # Se forneceu ano de início, perguntar sobre ano fim
                    ano_fim_val, ok4 = QInputDialog.getInt(self, 'Nova Série', 'Ano de fim (opcional):', 
                                                         ano_inicio if ano_inicio else 2000, 
                                                         ano_inicio if ano_inicio else 1800, 2100, 1)
                    if ok4:
                        ano_fim = str(ano_fim_val)
                
                serie_id = crud_series.adicionar_serie(
                    nome.strip(), descricao.strip(), 
                    str(ano_inicio) if ano_inicio else "", 
                    ano_fim, 
                    db_path=str(DB_PATH)
                )
                if serie_id:
                    QMessageBox.information(self, "Sucesso", "Série adicionada com sucesso!")
                    self.tabelar_series()
                else:
                    QMessageBox.warning(self, "Erro", "Falha ao adicionar série!")

    def abrir_serie(self):
        """Abrir detalhes da série selecionada"""
        selected = self.tableView_series.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            serie_id = self.tableView_series.model().index(row, 0).data()
            
            # Criar diálogo personalizado para exibir detalhes da série
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QWidget
            
            class DetalhesSerie(QDialog):
                def __init__(self, serie_id, parent=None):
                    super().__init__(parent)
                    self.serie_id = serie_id
                    self.setWindowTitle("Detalhes da Série")
                    self.setModal(True)
                    self.resize(800, 600)
                    self.setupUI()
                    self.carregar_dados()
                    
                def setupUI(self):
                    layout = QVBoxLayout(self)
                    
                    # Abas
                    tab_widget = QTabWidget()
                    
                    # Aba Informações
                    info_tab = QWidget()
                    info_layout = QVBoxLayout(info_tab)
                    
                    # Labels para informações da série
                    self.label_nome = QLabel()
                    self.label_nome.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
                    info_layout.addWidget(self.label_nome)
                    
                    self.label_descricao = QTextEdit()
                    self.label_descricao.setReadOnly(True)
                    self.label_descricao.setMaximumHeight(150)
                    info_layout.addWidget(QLabel("Descrição:"))
                    info_layout.addWidget(self.label_descricao)
                    
                    self.label_datas = QLabel()
                    info_layout.addWidget(self.label_datas)
                    
                    self.label_total = QLabel()
                    info_layout.addWidget(self.label_total)
                    
                    tab_widget.addTab(info_tab, "Informações")
                    
                    # Aba Pinturas
                    pinturas_tab = QWidget()
                    pinturas_layout = QVBoxLayout(pinturas_tab)
                    
                    self.tabela_pinturas = QTableWidget()
                    self.tabela_pinturas.setColumnCount(5)
                    self.tabela_pinturas.setHorizontalHeaderLabels(["ID", "Título", "Técnica", "Tamanho", "Data"])
                    pinturas_layout.addWidget(QLabel("Pinturas da Série:"))
                    pinturas_layout.addWidget(self.tabela_pinturas)
                    
                    tab_widget.addTab(pinturas_tab, "Pinturas")
                    
                    layout.addWidget(tab_widget)
                    
                    # Botões
                    button_layout = QHBoxLayout()
                    btn_fechar = QPushButton("Fechar")
                    btn_fechar.clicked.connect(self.close)
                    button_layout.addStretch()
                    button_layout.addWidget(btn_fechar)
                    layout.addLayout(button_layout)
                    
                def carregar_dados(self):
                    """Carregar dados da série"""
                    try:
                        serie = crud_series.buscar_serie(self.serie_id, db_path=str(DB_PATH))
                        if serie:
                            self.label_nome.setText(f"Série: {serie[1]}")
                            self.label_descricao.setPlainText(serie[2] or "Sem descrição")
                            
                            # Formatação das datas
                            data_inicio = serie[3] or "Não definida"
                            data_fim = serie[4] or "Não definida"
                            self.label_datas.setText(f"Período: {data_inicio} - {data_fim}")
                            
                            self.label_total.setText(f"Total de pinturas: {serie[5]}")
                            
                            # Carregar pinturas da série
                            pinturas = crud_series.listar_pinturas_da_serie(self.serie_id, db_path=str(DB_PATH))
                            self.tabela_pinturas.setRowCount(len(pinturas))
                            
                            for row, pintura in enumerate(pinturas):
                                for col, valor in enumerate(pintura):
                                    item = QTableWidgetItem(str(valor))
                                    self.tabela_pinturas.setItem(row, col, item)
                                    
                            # Ajustar largura das colunas
                            self.tabela_pinturas.resizeColumnsToContents()
                            
                    except Exception as e:
                        QMessageBox.warning(self, "Erro", f"Erro ao carregar série: {e}")
            
            detalhes = DetalhesSerie(serie_id, self)
            detalhes.exec_()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma série para abrir!")

    def editar_serie(self):
        """Editar série selecionada"""
        selected = self.tableView_series.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            serie_id = self.tableView_series.model().index(row, 0).data()
            
            # Buscar informações completas da série
            serie = crud_series.buscar_serie(serie_id, db_path=str(DB_PATH))
            if not serie:
                QMessageBox.warning(self, "Erro", "Série não encontrada!")
                return
                
            # Criar diálogo de edição usando o arquivo UI
            from PyQt5.QtWidgets import QDialog, QSpinBox
            
            class EditarSerieUI(QDialog):
                def __init__(self, serie_data, parent=None):
                    super().__init__(parent)
                    uic.loadUi(os.path.join(UI_DIR, 'Editar', 'Editar_série.ui'), self)
                    self.serie_data = serie_data
                    self.setWindowTitle("Editar Série")
                    self.setModal(True)
                    
                    # Configurar campos específicos para série
                    self.configurar_campos()
                    self.carregar_dados()
                    
                    # Conectar botões (assumindo que há OK/Cancel no UI)
                    if hasattr(self, 'buttonBox'):
                        self.buttonBox.accepted.connect(self.salvar)
                        self.buttonBox.rejected.connect(self.reject)
                    
                def configurar_campos(self):
                    """Configurar campos específicos para edição de séries"""
                    # Modificar labels e campos conforme necessário
                    if hasattr(self, 'checkBox'):
                        self.checkBox.setText("Nome")
                        self.checkBox.setChecked(True)
                    if hasattr(self, 'checkBox_2'):
                        self.checkBox_2.setText("Descrição")
                        self.checkBox_2.setChecked(False)
                    if hasattr(self, 'checkBox_3'):
                        self.checkBox_3.setText("Ano Início")
                        self.checkBox_3.setChecked(False)
                    if hasattr(self, 'checkBox_4'):
                        self.checkBox_4.setText("Ano Fim")
                        self.checkBox_4.setChecked(False)
                    
                def carregar_dados(self):
                    """Carregar dados da série nos campos"""
                    if hasattr(self, 'lineEdit'):
                        self.lineEdit.setText(self.serie_data[1])  # Nome
                    if hasattr(self, 'lineEdit_2'):
                        self.lineEdit_2.setText(self.serie_data[2] or "")  # Descrição
                    if hasattr(self, 'lineEdit_3'):
                        # Extrair apenas o ano da data de início
                        ano_inicio = ""
                        if self.serie_data[3]:
                            try:
                                ano_inicio = self.serie_data[3].split('-')[0]
                            except:
                                ano_inicio = str(self.serie_data[3])
                        self.lineEdit_3.setText(ano_inicio)
                    if hasattr(self, 'lineEdit_4'):
                        # Extrair apenas o ano da data de fim
                        ano_fim = ""
                        if self.serie_data[4]:
                            try:
                                ano_fim = self.serie_data[4].split('-')[0]
                            except:
                                ano_fim = str(self.serie_data[4])
                        self.lineEdit_4.setText(ano_fim)
                    
                def salvar(self):
                    """Salvar alterações"""
                    nome = ""
                    descricao = ""
                    ano_inicio = ""
                    ano_fim = ""
                    
                    # Coletar dados dos campos habilitados
                    if hasattr(self, 'checkBox') and self.checkBox.isChecked():
                        nome = self.lineEdit.text().strip()
                        if not nome:
                            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
                            return
                    else:
                        nome = self.serie_data[1]  # Manter nome atual
                    
                    if hasattr(self, 'checkBox_2') and self.checkBox_2.isChecked():
                        descricao = self.lineEdit_2.text().strip()
                    else:
                        descricao = self.serie_data[2] or ""
                    
                    if hasattr(self, 'checkBox_3') and self.checkBox_3.isChecked():
                        ano_inicio = self.lineEdit_3.text().strip()
                    else:
                        # Manter ano atual se existir
                        if self.serie_data[3]:
                            try:
                                ano_inicio = self.serie_data[3].split('-')[0]
                            except:
                                ano_inicio = str(self.serie_data[3])
                    
                    if hasattr(self, 'checkBox_4') and self.checkBox_4.isChecked():
                        ano_fim = self.lineEdit_4.text().strip()
                    else:
                        # Manter ano atual se existir
                        if self.serie_data[4]:
                            try:
                                ano_fim = self.serie_data[4].split('-')[0]
                            except:
                                ano_fim = str(self.serie_data[4])
                    
                    # Atualizar no banco
                    success = crud_series.atualizar_serie(
                        self.serie_data[0], nome, descricao, ano_inicio, ano_fim, 
                        db_path=str(DB_PATH)
                    )
                    
                    if success:
                        self.accept()
                    else:
                        QMessageBox.warning(self, "Erro", "Falha ao atualizar série!")
            
            dialog = EditarSerieUI(serie, self)
            if dialog.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Sucesso", "Série atualizada com sucesso!")
                self.tabelar_series()
                
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma série para editar!")

    def excluir_serie(self):
        """Excluir séries selecionadas (múltiplas seleções)"""
        selected = self.tableView_series.selectionModel().selectedRows()
        if selected:
            # Preparar lista de séries para exclusão
            series_para_excluir = []
            for index in selected:
                row = index.row()
                serie_id = self.tableView_series.model().index(row, 0).data()
                nome = self.tableView_series.model().index(row, 1).data()
                series_para_excluir.append((serie_id, nome))
            
            # Confirmar exclusão
            if len(series_para_excluir) == 1:
                nome = series_para_excluir[0][1]
                mensagem = f'Deseja realmente excluir a série "{nome}"?'
            else:
                nomes = [serie[1] for serie in series_para_excluir]
                mensagem = f'Deseja realmente excluir {len(series_para_excluir)} séries?\n\n' + '\n'.join(f'• {nome}' for nome in nomes[:5])
                if len(nomes) > 5:
                    mensagem += f'\n... e mais {len(nomes) - 5} séries'
            
            reply = QMessageBox.question(self, 'Confirmar Exclusão', 
                                       mensagem,
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                sucessos = 0
                erros = []
                
                for serie_id, nome in series_para_excluir:
                    success, message = crud_series.remover_serie(serie_id, db_path=str(DB_PATH))
                    if success:
                        sucessos += 1
                    else:
                        erros.append(f'{nome}: {message}')
                
                # Mostrar resultado
                if sucessos > 0 and len(erros) == 0:
                    QMessageBox.information(self, "Sucesso", 
                                          f"{sucessos} série(s) removida(s) com sucesso!")
                elif sucessos > 0 and len(erros) > 0:
                    QMessageBox.warning(self, "Parcial", 
                                      f"{sucessos} série(s) removida(s) com sucesso.\n\nErros:\n" + 
                                      '\n'.join(erros[:3]) + 
                                      (f'\n... e mais {len(erros) - 3} erros' if len(erros) > 3 else ''))
                else:
                    QMessageBox.warning(self, "Erro", 
                                      f"Nenhuma série foi removida.\n\nErros:\n" + 
                                      '\n'.join(erros[:3]) + 
                                      (f'\n... e mais {len(erros) - 3} erros' if len(erros) > 3 else ''))
                
                self.tabelar_series()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma ou mais séries para excluir!")

    def editar_exposicao(self):
        """Editar exposição selecionada"""
        selected = self.tableView_3.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            expo_id = self.tableView_3.model().index(row, 0).data()
            
            # Buscar dados da exposição
            from Funções.crud_exp import buscar_exposicao, atualizar_exposicao
            try:
                exposicao = buscar_exposicao(expo_id, db_path=str(DB_PATH))
                
                if not exposicao:
                    QMessageBox.warning(self, "Erro", "Exposição não encontrada!")
                    return
                
                # Criar diálogo de edição usando o arquivo UI
                from PyQt5.QtWidgets import QDialog
                
                class EditarExposicao(QDialog):
                    def __init__(self, exposicao_data, parent=None):
                        super().__init__(parent)
                        uic.loadUi(os.path.join(UI_DIR, 'Editar', 'Editar_expo.ui'), self)
                        self.exposicao_data = exposicao_data
                        self.setWindowTitle("Editar Exposição")
                        self.setModal(True)
                        self.configurar_campos()
                        self.carregar_dados()
                        
                        # Conectar botões
                        self.buttonBox.accepted.connect(self.salvar)
                        self.buttonBox.rejected.connect(self.reject)
                        
                    def configurar_campos(self):
                        """Configurar campos específicos para edição de exposições"""
                        # Configurar checkboxes e labels
                        if hasattr(self, 'checkBox'):
                            self.checkBox.setText("Nome")
                            self.checkBox.setChecked(True)
                        if hasattr(self, 'checkBox_2'):
                            self.checkBox_2.setText("Tema")
                            self.checkBox_2.setChecked(False)
                        if hasattr(self, 'checkBox_3'):
                            self.checkBox_3.setText("Data")
                            self.checkBox_3.setChecked(False)
                        if hasattr(self, 'checkBox_4'):
                            self.checkBox_4.setText("Local")
                            self.checkBox_4.setChecked(False)
                        if hasattr(self, 'checkBox_5'):
                            self.checkBox_5.setText("Curadoria")
                            self.checkBox_5.setChecked(False)
                        if hasattr(self, 'checkBox_6'):
                            self.checkBox_6.setText("Organizador")
                            self.checkBox_6.setChecked(False)
                        
                    def carregar_dados(self):
                        """Carregar dados da exposição nos campos"""
                        # exposicao_data = (id, nome, tema, artistas, data, local, curadoria, organizador)
                        if hasattr(self, 'lineEdit'):
                            self.lineEdit.setText(self.exposicao_data[1] or "")  # Nome
                        if hasattr(self, 'lineEdit_2'):
                            self.lineEdit_2.setText(self.exposicao_data[2] or "")  # Tema
                        if hasattr(self, 'lineEdit_3'):
                            self.lineEdit_3.setText(self.exposicao_data[4] or "")  # Data
                        if hasattr(self, 'lineEdit_4'):
                            self.lineEdit_4.setText(self.exposicao_data[5] or "")  # Local
                        # Adicionar campos para curadoria e organizador se existirem
                        
                    def salvar(self):
                        """Salvar alterações"""
                        try:
                            # Coletar dados dos campos habilitados
                            nome = self.exposicao_data[1]  # Manter nome atual por padrão
                            tema = self.exposicao_data[2] or ""
                            data = self.exposicao_data[4] or ""
                            local = self.exposicao_data[5] or ""
                            curadoria = self.exposicao_data[6] or ""
                            organizador = self.exposicao_data[7] or ""
                            artistas = self.exposicao_data[3] or ""
                            
                            if hasattr(self, 'checkBox') and self.checkBox.isChecked():
                                nome = self.lineEdit.text().strip()
                                if not nome:
                                    QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
                                    return
                            
                            if hasattr(self, 'checkBox_2') and self.checkBox_2.isChecked():
                                tema = self.lineEdit_2.text().strip()
                                
                            if hasattr(self, 'checkBox_3') and self.checkBox_3.isChecked():
                                data = self.lineEdit_3.text().strip()
                                
                            if hasattr(self, 'checkBox_4') and self.checkBox_4.isChecked():
                                local = self.lineEdit_4.text().strip()
                            
                            # Atualizar no banco
                            success = atualizar_exposicao(
                                self.exposicao_data[0], nome, tema, artistas, 
                                data, local, curadoria, organizador, 
                                db_path=str(DB_PATH)
                            )
                            
                            if success:
                                self.accept()
                            else:
                                QMessageBox.warning(self, "Erro", "Falha ao atualizar exposição!")
                        except Exception as e:
                            QMessageBox.warning(self, "Erro", f"Erro ao salvar: {e}")
                
                dialog = EditarExposicao(exposicao, self)
                if dialog.exec_() == QDialog.Accepted:
                    QMessageBox.information(self, "Sucesso", "Exposição atualizada com sucesso!")
                    self.tabelar_exposicoes()
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar exposição: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma exposição para editar!")

    def excluir_exposicao(self):
        """Excluir exposições selecionadas (múltiplas seleções)"""
        selected = self.tableView_3.selectionModel().selectedRows()
        if selected:
            # Preparar lista de exposições para exclusão
            exposicoes_para_excluir = []
            for index in selected:
                row = index.row()
                expo_id = self.tableView_3.model().index(row, 0).data()
                nome = self.tableView_3.model().index(row, 1).data()
                exposicoes_para_excluir.append((expo_id, nome))
            
            # Confirmar exclusão
            if len(exposicoes_para_excluir) == 1:
                nome = exposicoes_para_excluir[0][1]
                mensagem = f'Deseja realmente excluir a exposição "{nome}"?'
            else:
                nomes = [expo[1] for expo in exposicoes_para_excluir]
                mensagem = f'Deseja realmente excluir {len(exposicoes_para_excluir)} exposições?\n\n' + '\n'.join(f'• {nome}' for nome in nomes[:5])
                if len(nomes) > 5:
                    mensagem += f'\n... e mais {len(nomes) - 5} exposições'
            
            reply = QMessageBox.question(self, 'Confirmar Exclusão', 
                                       mensagem,
                                       QMessageBox.Yes | QMessageBox.No, 
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                from Funções.crud_exp import remover_exposicao
                sucessos = 0
                erros = []
                
                for expo_id, nome in exposicoes_para_excluir:
                    success, message = remover_exposicao(expo_id, db_path=str(DB_PATH))
                    if success:
                        sucessos += 1
                    else:
                        erros.append(f'{nome}: {message}')
                
                # Mostrar resultado
                if sucessos > 0 and len(erros) == 0:
                    QMessageBox.information(self, "Sucesso", 
                                          f"{sucessos} exposição(ões) removida(s) com sucesso!")
                elif sucessos > 0 and len(erros) > 0:
                    QMessageBox.warning(self, "Parcial", 
                                      f"{sucessos} exposição(ões) removida(s) com sucesso.\n\nErros:\n" + 
                                      '\n'.join(erros[:3]) + 
                                      (f'\n... e mais {len(erros) - 3} erros' if len(erros) > 3 else ''))
                else:
                    QMessageBox.warning(self, "Erro", 
                                      f"Nenhuma exposição foi removida.\n\nErros:\n" + 
                                      '\n'.join(erros[:3]) + 
                                      (f'\n... e mais {len(erros) - 3} erros' if len(erros) > 3 else ''))
                
                self.tabelar_exposicoes()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma ou mais exposições para excluir!")

    def gerenciar_obras_exposicao(self):
        """Gerenciar obras de uma exposição"""
        selected = self.tableView_3.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            expo_id = self.tableView_3.model().index(row, 0).data()
            expo_nome = self.tableView_3.model().index(row, 1).data()
            
            # Criar diálogo para gerenciar obras
            from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                                       QWidget, QListWidget, QListWidgetItem, QPushButton, 
                                       QLabel, QCheckBox)
            
            class GerenciarObras(QDialog):
                def __init__(self, exposicao_id, exposicao_nome, parent=None):
                    super().__init__(parent)
                    self.exposicao_id = exposicao_id
                    self.setWindowTitle(f"Gerenciar Obras - {exposicao_nome}")
                    self.setModal(True)
                    self.resize(700, 500)
                    self.setupUI()
                    self.carregar_dados()
                    
                def setupUI(self):
                    layout = QVBoxLayout(self)
                    
                    # Abas
                    tab_widget = QTabWidget()
                    
                    # Aba - Obras na Exposição
                    obras_expo_tab = QWidget()
                    obras_expo_layout = QVBoxLayout(obras_expo_tab)
                    
                    obras_expo_layout.addWidget(QLabel("Obras atualmente na exposição:"))
                    self.lista_obras_expo = QListWidget()
                    obras_expo_layout.addWidget(self.lista_obras_expo)
                    
                    btn_remover = QPushButton("Remover da Exposição")
                    btn_remover.clicked.connect(self.remover_obra)
                    obras_expo_layout.addWidget(btn_remover)
                    
                    tab_widget.addTab(obras_expo_tab, "Obras na Exposição")
                    
                    # Aba - Adicionar Obras
                    adicionar_tab = QWidget()
                    adicionar_layout = QVBoxLayout(adicionar_tab)
                    
                    adicionar_layout.addWidget(QLabel("Todas as pinturas disponíveis:"))
                    self.lista_todas_obras = QListWidget()
                    adicionar_layout.addWidget(self.lista_todas_obras)
                    
                    btn_adicionar = QPushButton("Adicionar à Exposição")
                    btn_adicionar.clicked.connect(self.adicionar_obra)
                    adicionar_layout.addWidget(btn_adicionar)
                    
                    tab_widget.addTab(adicionar_tab, "Adicionar Obras")
                    
                    layout.addWidget(tab_widget)
                    
                    # Botões
                    button_layout = QHBoxLayout()
                    btn_fechar = QPushButton("Fechar")
                    btn_fechar.clicked.connect(self.close)
                    button_layout.addStretch()
                    button_layout.addWidget(btn_fechar)
                    layout.addLayout(button_layout)
                    
                def carregar_dados(self):
                    """Carregar obras da exposição e todas as pinturas"""
                    try:
                        # Carregar obras já na exposição
                        from Funções.crud_pinturas_exposicoes import listar_pinturas_exposicao
                        obras_expo = listar_pinturas_exposicao(self.exposicao_id, db_path=str(DB_PATH))
                        
                        self.lista_obras_expo.clear()
                        for obra in obras_expo:
                            item = QListWidgetItem(f"{obra[0]} - {obra[1]}")  # id - título
                            item.setData(32, obra[0])  # Qt.UserRole
                            self.lista_obras_expo.addItem(item)
                        
                        # Carregar todas as pinturas
                        from Funções.crud_pint import listar_pinturas
                        todas_pinturas = listar_pinturas(db_path=str(DB_PATH))
                        
                        self.lista_todas_obras.clear()
                        for pintura in todas_pinturas:
                            item = QListWidgetItem(f"{pintura[0]} - {pintura[1]}")  # id - título
                            item.setData(32, pintura[0])  # Qt.UserRole
                            self.lista_todas_obras.addItem(item)
                            
                    except Exception as e:
                        QMessageBox.warning(self, "Erro", f"Erro ao carregar dados: {e}")
                    
                def adicionar_obra(self):
                    """Adicionar obra selecionada à exposição"""
                    current_item = self.lista_todas_obras.currentItem()
                    if current_item:
                        pintura_id = current_item.data(32)
                        
                        try:
                            from Funções.crud_pinturas_exposicoes import associar_pintura_exposicao
                            success = associar_pintura_exposicao(pintura_id, self.exposicao_id, db_path=str(DB_PATH))
                            if success:
                                QMessageBox.information(self, "Sucesso", "Obra adicionada à exposição!")
                                self.carregar_dados()  # Recarregar
                            else:
                                QMessageBox.warning(self, "Aviso", "Obra já está na exposição ou erro ao adicionar!")
                        except Exception as e:
                            QMessageBox.warning(self, "Erro", f"Erro ao adicionar obra: {e}")
                    else:
                        QMessageBox.warning(self, "Aviso", "Selecione uma obra para adicionar!")
                
                def remover_obra(self):
                    """Remover obra selecionada da exposição"""
                    current_item = self.lista_obras_expo.currentItem()
                    if current_item:
                        pintura_id = current_item.data(32)
                        
                        reply = QMessageBox.question(self, 'Confirmar Remoção', 
                                                   'Deseja remover esta obra da exposição?',
                                                   QMessageBox.Yes | QMessageBox.No, 
                                                   QMessageBox.No)
                        
                        if reply == QMessageBox.Yes:
                            try:
                                from Funções.crud_pinturas_exposicoes import remover_pintura_exposicao
                                success = remover_pintura_exposicao(pintura_id, self.exposicao_id, db_path=str(DB_PATH))
                                if success:
                                    QMessageBox.information(self, "Sucesso", "Obra removida da exposição!")
                                    self.carregar_dados()  # Recarregar
                                else:
                                    QMessageBox.warning(self, "Erro", "Erro ao remover obra!")
                            except Exception as e:
                                QMessageBox.warning(self, "Erro", f"Erro ao remover obra: {e}")
                    else:
                        QMessageBox.warning(self, "Aviso", "Selecione uma obra para remover!")
            
            dialog = GerenciarObras(expo_id, expo_nome, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma exposição para gerenciar obras!")

    def on_serie_selected(self):
        """Atualizar detalhes quando uma série é selecionada"""
        selected = self.tableView_series.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            serie_id = self.tableView_series.model().index(row, 0).data()
            
            # Buscar detalhes da série
            try:
                serie = crud_series.buscar_serie(serie_id, db_path=str(DB_PATH))
                
                if serie:
                    # Atualizar labels da aba Séries
                    self.label_seriesTitulo.setText(serie[1])  # Nome
                    self.label_seriesNomeValor.setText(serie[1])  # Nome
                    self.label_seriesDescricaoValor.setText(serie[2] if serie[2] else "Sem descrição")  # Descrição
                    
                    # Período
                    periodo = ""
                    if serie[3] and serie[4]:  # ano_inicio e ano_fim
                        periodo = f"{serie[3]} - {serie[4]}"
                    elif serie[3]:  # apenas ano_inicio
                        periodo = f"Desde {serie[3]}"
                    else:
                        periodo = "Período não definido"
                    
                    self.label_seriesPeriodoValor.setText(periodo)
                    self.label_seriesPinturasValor.setText(f"{serie[5]} pintura(s)")  # total_pinturas
                else:
                    # Limpar labels se série não encontrada
                    self.label_seriesTitulo.setText("")
                    self.label_seriesNomeValor.setText("")
                    self.label_seriesDescricaoValor.setText("")
                    self.label_seriesPeriodoValor.setText("")
                    self.label_seriesPinturasValor.setText("")
                    
            except Exception as e:
                print(f"Erro ao buscar série: {e}")
                # Limpar labels em caso de erro
                self.label_seriesTitulo.setText("")
                self.label_seriesNomeValor.setText("")
                self.label_seriesDescricaoValor.setText("")
                self.label_seriesPeriodoValor.setText("")
                self.label_seriesPinturasValor.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    




    

