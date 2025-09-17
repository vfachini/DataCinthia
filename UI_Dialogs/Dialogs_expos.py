# -*- coding: utf-8 -*-
"""
Diálogos para operações com exposições
Classes de diálogo para adicionar, editar e visualizar exposições
"""

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QTableWidgetItem, QMessageBox, QListWidgetItem, QVBoxLayout, QListWidget, QLabel, QPushButton
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
import sys
from pathlib import Path  

# Adicionar o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

from Funções.crud_exp import adicionar_exposicao
from Funções.crud_pinturas_exposicoes import associar_pintura_exposicao, remover_pintura_exposicao, mostrar_detalhes_exposicao, listar_obras_exposicao
from Funções.detalhes_pintura import mostrar_detalhes

BASE_DIR = Path(__file__).parent.parent.resolve()
UI_DIR   = BASE_DIR / "Interface"
DB_PATH  = BASE_DIR / "Data" / "Data.db"

class Nova_exposicao(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Adicionar", "Exposicao.ui"), self)
        self.setWindowTitle("Nova Exposição")
        self.btnSalvar = self.findChild(QPushButton, 'btnSalvar')
        self.btnCancelar = self.findChild(QPushButton, 'btnCancelar')
        self.btnSalvar.clicked.connect(self.adicionar)
        self.btnCancelar.clicked.connect(self.reject)




    def adicionar(self):
        # Coletar dados dos campos do UI modernizado
        titulo = self.nome.text().strip()
        tema = self.tema.text().strip()
        data_inicio = self.data.date().toString("dd/MM/yyyy")
        local = self.local.text().strip()
        curadoria = self.curadoria.text().strip()
        organizacao = self.organizador.text().strip()
        
        # Valores padrão
        tipo = "Individual"  # Pode ser ajustado depois
        artistas = ""  # Pode ser ajustado depois
        periodo = None
        
        if not titulo:
            QMessageBox.warning(self, "Erro", "Nome da exposição é obrigatório!")
            return
            
        try:
            #ordem de def adicionar_exposicao(nome, tema, tipo, artistas, data, local, curadoria, organizador, periodo=None):
            exposicao_id = adicionar_exposicao(titulo, tema, tipo, artistas, data_inicio, local, curadoria, organizacao, periodo)
            
            # Mostrar diálogo de pasta criada
            dialog_pasta = Exposicao_caminho(exposicao_id, titulo)
            dialog_pasta.exec_()
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar exposição: {str(e)}")


    def clear(self):
        self.lineEdit_titulo.clear()
        self.dateEdit_inicio.setDate(self.dateEdit_inicio.minimumDate())
        self.lineEdit_local.clear()

class Abrir_exposicao(QDialog):
    def __init__(self, exposicao_id):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Abrir", "Exposicao.ui"), self)
        self.setWindowTitle("Visualizar Exposição")
        self.exposicao_id = exposicao_id
        
        # Conectar botões e eventos
        self.conectar_eventos()
        
        # Carregar dados da exposição
        self.carregar_dados_exposicao()
        self.preencher_lista_obras()

    def conectar_eventos(self):
        # Botões principais
        self.buttonBox_Expo_OP.accepted.connect(self.accept)
        self.buttonBox_Expo_OP.rejected.connect(self.reject)
        
        # Lista de obras e seleção
        self.Art_expo_list.itemSelectionChanged.connect(self.obra_selecionada)
        self.comboBox.currentTextChanged.connect(self.foto_mudou)
        
        # Botões de ação
        self.RemovefromExpo.clicked.connect(self.remover_obra)
        self.Add_a_expo.clicked.connect(self.adicionar_obras)

    def carregar_dados_exposicao(self):
        # Buscar detalhes da exposição no banco
        detalhes = mostrar_detalhes_exposicao(self.exposicao_id, db_path=str(DB_PATH))
        
        if detalhes:
            # Preencher título principal
            self.label.setText(detalhes["exposicao"][1])  # nome da exposição
            
            # Preencher painel de informações
            self.label_42.setText(detalhes["exposicao"][1])  # título
            self.label_33.setText(detalhes["exposicao"][2] or "Sem tema")  # tema
            self.label_35.setText(detalhes["exposicao"][5])  # data
            self.label_39.setText(detalhes["exposicao"][6] or "Sem curador")  # curadoria
            self.label_17.setText(detalhes["exposicao"][7] or "Local não informado")  # local
            
            # Contar número de obras
            numero_obras = len(detalhes.get("obras", []))
            self.label_37.setText(str(numero_obras))

    def preencher_lista_obras(self):
        # Limpar lista atual
        self.Art_expo_list.clear()
        
        # Buscar obras da exposição
        obras = listar_obras_exposicao(self.exposicao_id, db_path=str(DB_PATH))
        
        if obras:
            for obra in obras:
                # Criar item da lista: "ID - Título"
                texto_item = f"{obra[0]} - {obra[1]}"
                item = QListWidgetItem(texto_item)
                item.setData(Qt.UserRole, obra[0])  # guardar ID da obra
                self.Art_expo_list.addItem(item)
        else:
            # Mensagem quando não há obras
            item = QListWidgetItem("Nenhuma obra encontrada")
            item.setFlags(Qt.NoItemFlags)  # não selecionável
            self.Art_expo_list.addItem(item)

    def obra_selecionada(self):
        # Verificar se tem item selecionado
        item_atual = self.Art_expo_list.currentItem()
        if not item_atual:
            return
            
        # Pegar ID da obra selecionada
        obra_id = item_atual.data(Qt.UserRole)
        if obra_id:
            # Carregar fotos da obra
            self.carregar_fotos_obra(obra_id)
            # Mostrar primeira foto
            self.mostrar_primeira_foto()

    def carregar_fotos_obra(self, obra_id):
        # Limpar combobox de fotos
        self.comboBox.clear()
        
        # Buscar detalhes da obra para pegar caminho das fotos
        detalhes_obra = mostrar_detalhes(obra_id, db_path=str(DB_PATH))
        fotos_path = detalhes_obra.get("fotos_path")
        
        if fotos_path and os.path.exists(fotos_path):
            # Listar arquivos de foto
            for foto in os.listdir(fotos_path):
                if foto.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.comboBox.addItem(foto)
        else:
            # Sem fotos disponíveis
            self.comboBox.addItem("Sem fotos")

    def foto_mudou(self, nome_foto):
        # Quando muda a foto selecionada
        if nome_foto and nome_foto != "Sem fotos":
            self.mostrar_foto(nome_foto)

    def mostrar_foto(self, nome_foto):
        # Pegar obra selecionada
        item_atual = self.Art_expo_list.currentItem()
        if not item_atual:
            return
            
        obra_id = item_atual.data(Qt.UserRole)
        if obra_id:
            # Buscar caminho das fotos
            detalhes_obra = mostrar_detalhes(obra_id, db_path=str(DB_PATH))
            fotos_path = detalhes_obra.get("fotos_path")
            
            if fotos_path:
                caminho_completo = os.path.join(fotos_path, nome_foto)
                if os.path.exists(caminho_completo):
                    # Carregar e redimensionar foto
                    pixmap = QPixmap(caminho_completo).scaled(400, 400, Qt.KeepAspectRatio)
                    self.Imagens_expo_selecionadas.setPixmap(pixmap)
                else:
                    self.Imagens_expo_selecionadas.setText("Foto não encontrada")
            else:
                self.Imagens_expo_selecionadas.setText("Sem fotos")

    def mostrar_primeira_foto(self):
        # Mostrar primeira foto automaticamente
        if self.comboBox.count() > 0:
            primeira_foto = self.comboBox.itemText(0)
            if primeira_foto != "Sem fotos":
                self.mostrar_foto(primeira_foto)

    def remover_obra(self):
        # Pegar obra selecionada
        item_atual = self.Art_expo_list.currentItem()
        if not item_atual:
            QMessageBox.warning(self, "Aviso", "Selecione uma obra para remover!")
            return
            
        obra_id = item_atual.data(Qt.UserRole)
        if obra_id:
            # Confirmar remoção
            resposta = QMessageBox.question(
                self, "Confirmar", 
                f"Remover obra '{item_atual.text()}' desta exposição?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if resposta == QMessageBox.Yes:
                # Remover obra da exposição (não deletar a obra)
                remover_pintura_exposicao(obra_id, self.exposicao_id, db_path=str(DB_PATH))
                QMessageBox.information(self, "Sucesso", "Obra removida da exposição!")
                
                # Atualizar lista
                self.preencher_lista_obras()
                self.limpar_exibicao_foto()

    def adicionar_obras(self):
        # Abrir diálogo para adicionar obras
        dialog = Selecionar_obras_para_exposicao(self.exposicao_id)
        if dialog.exec_() == QDialog.Accepted:
            # Atualizar lista após adicionar
            self.preencher_lista_obras()
            QMessageBox.information(self, "Sucesso", "Obras adicionadas à exposição!")

    def limpar_exibicao_foto(self):
        # Limpar exibição de foto
        self.Imagens_expo_selecionadas.setText("Imagens")
        self.comboBox.clear()


class Selecionar_obras_para_exposicao(QDialog):
    """Diálogo para selecionar obras e adicionar a uma exposição"""
    def __init__(self, exposicao_id):
        super().__init__()
        # Para agora, criar um diálogo simples
        self.setWindowTitle("Selecionar Obras para Exposição")
        self.exposicao_id = exposicao_id
        self.setModal(True)
        
        # Configurar layout básico
        layout = QVBoxLayout()
        
        # Lista de obras disponíveis (você pode expandir isso)
        self.lista_obras = QListWidget()
        layout.addWidget(QLabel("Obras disponíveis:"))
        layout.addWidget(self.lista_obras)
        
        # Botões
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.adicionar_selecionadas)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)
        
        self.setLayout(layout)
        self.carregar_obras_disponiveis()
    
    def carregar_obras_disponiveis(self):
        # Carregar todas as obras que ainda não estão na exposição
        from Funções.crud_pint import listar_pinturas
        todas_obras = listar_pinturas(db_path=str(DB_PATH))
        obras_exposicao = listar_obras_exposicao(self.exposicao_id, db_path=str(DB_PATH))
        obras_na_expo = [obra[0] for obra in obras_exposicao]
        
        for obra in todas_obras:
            if obra[0] not in obras_na_expo:  # obra não está na exposição
                item = QListWidgetItem(f"{obra[0]} - {obra[1]}")
                item.setData(Qt.UserRole, obra[0])
                self.lista_obras.addItem(item)
    
    def adicionar_selecionadas(self):
        # Adicionar obras selecionadas à exposição
        items_selecionados = self.lista_obras.selectedItems()
        
        if not items_selecionados:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos uma obra!")
            return
        
        for item in items_selecionados:
            obra_id = item.data(Qt.UserRole)
            associar_pintura_exposicao(obra_id, self.exposicao_id, db_path=str(DB_PATH))
        
        self.accept()

class Exposicao_caminho(QDialog):
    def __init__(self, exposicao_id, nome_exposicao):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Adicionar", 'Pintura_caminho.ui'), self)
        self.exposicao_id = exposicao_id
        
        # Personalizar para exposição
        self.setWindowTitle("Pasta Criada - Organize sua Exposição")
        
        # Obter caminho da pasta criada
        try:
            from Funções.gerenciador_pastas import gerenciador_pastas
            pasta_exposicao = gerenciador_pastas.obter_pasta_exposicao(exposicao_id, nome_exposicao)
            if pasta_exposicao:
                self.Caminho.setText(pasta_exposicao)
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


class Pesquisa_exposicao(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Buscar", 'Pesquisa_exposicao.ui'), self)
        
        # Conectar botões
        self.btnBuscar.clicked.connect(self.buscar)
        self.btnLimpar.clicked.connect(self.limpar)
        self.btnAbrir.clicked.connect(self.abrir_exposicao_selecionada)
        self.btnFechar.clicked.connect(self.reject)

        # ID selecionado via diálogo
        self.selected_exposicao_id = None

        # Conectar seleção da tabela
        self.tabelaResultados.itemSelectionChanged.connect(self.on_selection_changed)

        # Configurar tabela
        self.configurar_tabela()

        # Carregar todas as exposições inicialmente
        self.carregar_todas_exposicoes()

    def configurar_tabela(self):
        """Configurar a tabela de resultados"""
        self.tabelaResultados.setColumnWidth(0, 50)   # ID
        self.tabelaResultados.setColumnWidth(1, 200)  # Nome
        self.tabelaResultados.setColumnWidth(2, 80)   # Data
        self.tabelaResultados.setColumnWidth(3, 150)  # Local
        self.tabelaResultados.setColumnWidth(4, 60)   # Obras

    def carregar_todas_exposicoes(self):
        """Carregar todas as exposições na tabela"""
        try:
            from Funções.crud_exp import listar_exposicoes
            exposicoes = listar_exposicoes()
            self.preencher_tabela(exposicoes)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar exposições: {str(e)}")

    def buscar(self):
        """Realizar busca com filtros"""
        # Coletar filtros
        nome = self.nome.text().strip() if self.nome.text() else None
        local = self.local.text().strip() if self.local.text() else None
        ano = self.ano.value() if self.ano.value() != self.ano.minimum() else None
        apenas_ativas = self.checkAtiva.isChecked()
        
        try:
            # Buscar com filtros
            from Funções.crud_exp import buscar_exposicoes_filtros
            resultados = buscar_exposicoes_filtros(nome, local, ano, apenas_ativas)
            self.preencher_tabela(resultados)
            
            if not resultados:
                QMessageBox.information(self, "Busca", "Nenhuma exposição encontrada com os filtros especificados.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na busca: {str(e)}")

    def preencher_tabela(self, exposicoes):
        """Preencher tabela com resultados"""
        self.tabelaResultados.setRowCount(len(exposicoes))
        
        for row, exposicao in enumerate(exposicoes):
            # exposicao = (id, nome, data, local, total_obras)
            self.tabelaResultados.setItem(row, 0, QTableWidgetItem(str(exposicao[0])))
            self.tabelaResultados.setItem(row, 1, QTableWidgetItem(str(exposicao[1])))
            self.tabelaResultados.setItem(row, 2, QTableWidgetItem(str(exposicao[2]) if exposicao[2] else ""))
            self.tabelaResultados.setItem(row, 3, QTableWidgetItem(str(exposicao[3]) if exposicao[3] else ""))
            total_obras = exposicao[4] if len(exposicao) > 4 else 0
            self.tabelaResultados.setItem(row, 4, QTableWidgetItem(str(total_obras)))

    def limpar(self):
        """Limpar filtros e recarregar todas as exposições"""
        self.nome.clear()
        self.local.clear()
        self.ano.setValue(self.ano.minimum())
        self.checkAtiva.setChecked(False)
        self.carregar_todas_exposicoes()

    def on_selection_changed(self):
        """Habilitar/desabilitar botão Abrir baseado na seleção"""
        tem_selecao = len(self.tabelaResultados.selectedItems()) > 0
        self.btnAbrir.setEnabled(tem_selecao)

    def abrir_exposicao_selecionada(self):
        """Abrir detalhes da exposição selecionada"""
        current_row = self.tabelaResultados.currentRow()
        if current_row >= 0:
            exposicao_id = int(self.tabelaResultados.item(current_row, 0).text())
            
            # Armazenar ID selecionado e aceitar diálogo para que o chamador saiba
            self.selected_exposicao_id = exposicao_id
            self.accept()
            return exposicao_id
        
        return None
