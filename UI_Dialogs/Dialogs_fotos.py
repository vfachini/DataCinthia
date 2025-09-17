# -*- coding: utf-8 -*-
"""
Diálogo para Gestão Visual de Fotos
Interface para upload, visualização e gerenciamento de fotos das pinturas
"""

import os
import shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

# Configurar diretório das interfaces
current_dir = os.path.dirname(__file__)
UI_DIR = os.path.join(os.path.dirname(current_dir), "Interface")


class GestaoFotos(QDialog):
    def __init__(self, pintura_id, nome_pintura):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, 'Gestao_fotos.ui'), self)
        
        self.pintura_id = pintura_id
        self.nome_pintura = nome_pintura
        self.pasta_pintura = None
        
        # Configurar título
        self.lblTitulo.setText(f"Gestão de Fotos - Pintura: {nome_pintura}")
        
        # Obter pasta da pintura
        self.obter_pasta_pintura()
        
        # Conectar eventos
        self.conectar_eventos()
        
        # Carregar fotos existentes
        self.carregar_fotos()
        
        # Configurar splitter (30% lista, 70% visualização)
        self.splitter.setSizes([270, 630])

    def conectar_eventos(self):
        """Conectar todos os eventos da interface"""
        self.btnAdicionarFoto.clicked.connect(self.adicionar_foto)
        self.btnRemoverFoto.clicked.connect(self.remover_foto)
        self.btnEditarDescricao.clicked.connect(self.editar_descricao)
        self.btnAbrirPasta.clicked.connect(self.abrir_pasta)
        self.listaFotos.itemSelectionChanged.connect(self.on_foto_selecionada)
        self.listaFotos.itemDoubleClicked.connect(self.visualizar_foto_completa)

    def obter_pasta_pintura(self):
        """Obter caminho da pasta da pintura"""
        try:
            from Funções.gerenciador_pastas import gerenciador_pastas
            self.pasta_pintura = gerenciador_pastas.obter_pasta_pintura(self.pintura_id, self.nome_pintura)
            
            if not self.pasta_pintura or not os.path.exists(self.pasta_pintura):
                QMessageBox.warning(self, "Aviso", "Pasta da pintura não encontrada. Algumas funcionalidades podem estar limitadas.")
                self.btnAbrirPasta.setEnabled(False)
                
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao obter pasta da pintura: {str(e)}")
            self.btnAbrirPasta.setEnabled(False)

    def carregar_fotos(self):
        """Carregar lista de fotos da pintura"""
        try:
            from Funções.crud_fotos import listar_fotos
            fotos = listar_fotos(self.pintura_id)
            
            self.listaFotos.clear()
            
            for foto in fotos:
                foto_id, caminho, descricao = foto
                
                # Criar item da lista
                item = QListWidgetItem()
                
                # Verificar se arquivo existe
                if os.path.exists(caminho):
                    nome_arquivo = os.path.basename(caminho)
                    item.setText(f"{nome_arquivo}")
                    item.setData(Qt.UserRole, foto)  # Armazenar dados da foto
                    
                    # Adicionar tooltip com descrição
                    tooltip = f"Arquivo: {nome_arquivo}"
                    if descricao:
                        tooltip += f"\nDescrição: {descricao}"
                    item.setToolTip(tooltip)
                    
                else:
                    # Arquivo não encontrado
                    nome_arquivo = os.path.basename(caminho)
                    item.setText(f"ERRO: {nome_arquivo} (nao encontrado)")
                    item.setData(Qt.UserRole, foto)
                    item.setForeground(QColor(200, 0, 0))  # Texto vermelho
                    
                self.listaFotos.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar fotos: {str(e)}")

    def on_foto_selecionada(self):
        """Evento quando uma foto é selecionada"""
        current_item = self.listaFotos.currentItem()
        
        if current_item:
            self.btnRemoverFoto.setEnabled(True)
            self.btnEditarDescricao.setEnabled(True)
            
            # Obter dados da foto
            foto_data = current_item.data(Qt.UserRole)
            if foto_data:
                foto_id, caminho, descricao = foto_data
                
                # Atualizar descrição
                desc_text = f"Descrição: {descricao}" if descricao else "Descrição: (sem descrição)"
                self.lblDescricao.setText(desc_text)
                
                # Carregar e exibir imagem
                self.carregar_imagem(caminho)
        else:
            self.btnRemoverFoto.setEnabled(False)
            self.btnEditarDescricao.setEnabled(False)
            self.lblDescricao.setText("Descrição: ")
            self.lblImagem.setText("Selecione uma foto para visualizar")
            self.lblImagem.setPixmap(QPixmap())

    def carregar_imagem(self, caminho):
        """Carregar e exibir imagem"""
        try:
            if os.path.exists(caminho):
                pixmap = QPixmap(caminho)
                if not pixmap.isNull():
                    # Redimensionar mantendo proporção
                    scaled_pixmap = pixmap.scaled(
                        self.lblImagem.size(), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.lblImagem.setPixmap(scaled_pixmap)
                    self.lblImagem.setText("")
                else:
                    self.lblImagem.setText("❌ Erro ao carregar imagem")
                    self.lblImagem.setPixmap(QPixmap())
            else:
                self.lblImagem.setText("❌ Arquivo não encontrado")
                self.lblImagem.setPixmap(QPixmap())
                
        except Exception as e:
            self.lblImagem.setText(f"❌ Erro: {str(e)}")
            self.lblImagem.setPixmap(QPixmap())

    def adicionar_foto(self):
        """Adicionar nova foto"""
        if not self.pasta_pintura:
            QMessageBox.warning(self, "Erro", "Pasta da pintura não disponível.")
            return
            
        # Abrir diálogo de seleção de arquivo
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Foto",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;Todos os arquivos (*)"
        )
        
        if arquivo:
            try:
                # Obter descrição
                descricao, ok = QInputDialog.getText(
                    self, 
                    "Descrição da Foto", 
                    "Digite uma descrição para a foto (opcional):"
                )
                
                if not ok:
                    return
                
                # Pasta de destino simples
                pasta_destino = os.path.join(self.pasta_pintura, "Fotos")
                
                # Garantir que a pasta existe
                os.makedirs(pasta_destino, exist_ok=True)
                
                # Copiar arquivo para pasta de destino
                nome_arquivo = os.path.basename(arquivo)
                caminho_destino = os.path.join(pasta_destino, nome_arquivo)
                
                # Verificar se já existe
                contador = 1
                nome_base, extensao = os.path.splitext(nome_arquivo)
                while os.path.exists(caminho_destino):
                    novo_nome = f"{nome_base}_{contador}{extensao}"
                    caminho_destino = os.path.join(pasta_destino, novo_nome)
                    contador += 1
                
                # Copiar arquivo
                shutil.copy2(arquivo, caminho_destino)
                
                # Adicionar ao banco de dados
                from Funções.crud_fotos import adicionar_foto
                adicionar_foto(self.pintura_id, caminho_destino, descricao or None)
                
                # Recarregar lista
                self.carregar_fotos()
                
                QMessageBox.information(self, "Sucesso", "Foto adicionada com sucesso!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao adicionar foto: {str(e)}")

    def remover_foto(self):
        """Remover foto selecionada"""
        current_item = self.listaFotos.currentItem()
        
        if not current_item:
            return
            
        foto_data = current_item.data(Qt.UserRole)
        if not foto_data:
            return
            
        foto_id, caminho, descricao = foto_data
        nome_arquivo = os.path.basename(caminho)
        
        # Confirmar remoção
        resposta = QMessageBox.question(
            self,
            "Confirmar Remoção",
            f"Deseja remover a foto '{nome_arquivo}'?\n\n" +
            "Isso removerá a referência do banco de dados.\n" +
            "O arquivo físico será mantido na pasta.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            try:
                from Funções.crud_fotos import remover_foto
                remover_foto(foto_id)
                
                # Recarregar lista
                self.carregar_fotos()
                
                QMessageBox.information(self, "Sucesso", "Foto removida do banco de dados!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao remover foto: {str(e)}")

    def editar_descricao(self):
        """Editar descrição da foto selecionada"""
        current_item = self.listaFotos.currentItem()
        
        if not current_item:
            return
            
        foto_data = current_item.data(Qt.UserRole)
        if not foto_data:
            return
            
        foto_id, caminho, descricao_atual = foto_data
        
        # Obter nova descrição
        nova_descricao, ok = QInputDialog.getText(
            self,
            "Editar Descrição",
            "Digite a nova descrição:",
            text=descricao_atual or ""
        )
        
        if ok:
            try:
                from Funções.crud_fotos import editar_descriçao
                editar_descriçao(foto_id, nova_descricao or None)
                
                # Recarregar lista
                self.carregar_fotos()
                
                QMessageBox.information(self, "Sucesso", "Descrição atualizada!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao editar descrição: {str(e)}")

    def abrir_pasta(self):
        """Abrir pasta da pintura no explorador"""
        if self.pasta_pintura and os.path.exists(self.pasta_pintura):
            os.startfile(self.pasta_pintura)  # Windows
        else:
            QMessageBox.warning(self, "Erro", "Pasta não encontrada!")

    def visualizar_foto_completa(self, item):
        """Visualizar foto em tamanho completo (duplo clique)"""
        foto_data = item.data(Qt.UserRole)
        if not foto_data:
            return
            
        foto_id, caminho, descricao = foto_data
        
        if os.path.exists(caminho):
            # Abrir arquivo com aplicativo padrão
            os.startfile(caminho)  # Windows
        else:
            QMessageBox.warning(self, "Erro", "Arquivo não encontrado!")
