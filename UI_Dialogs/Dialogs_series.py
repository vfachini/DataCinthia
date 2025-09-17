# -*- coding: utf-8 -*-
"""
Diálogos para operações com séries
Classes de diálogo para buscar séries
"""

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt
import os
import sys
from pathlib import Path  

# Adicionar o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

from Funções.crud_series import listar_series, buscar_series_filtros

BASE_DIR = Path(__file__).parent.parent.resolve()
UI_DIR   = BASE_DIR / "Interface"


class Pesquisa_serie(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Buscar", 'Pesquisa_serie.ui'), self)
        
        # ID selecionado via diálogo de busca
        self.selected_serie_id = None
        
        # Conectar botões
        self.btnBuscar.clicked.connect(self.buscar)
        self.btnLimpar.clicked.connect(self.limpar)
        self.btnAbrir.clicked.connect(self.abrir_serie_selecionada)
        self.btnFechar.clicked.connect(self.reject)
        
        # Conectar seleção da tabela
        self.tabelaResultados.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Configurar tabela
        self.configurar_tabela()
        
        # Carregar todas as séries inicialmente
        self.carregar_todas_series()

    def configurar_tabela(self):
        """Configurar a tabela de resultados"""
        self.tabelaResultados.setColumnWidth(0, 50)   # ID
        self.tabelaResultados.setColumnWidth(1, 200)  # Nome
        self.tabelaResultados.setColumnWidth(2, 80)   # Ano Início
        self.tabelaResultados.setColumnWidth(3, 80)   # Ano Fim

    def carregar_todas_series(self):
        """Carregar todas as séries na tabela"""
        try:
            series = listar_series()
            self.preencher_tabela(series)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar séries: {str(e)}")

    def buscar(self):
        """Realizar busca com filtros"""
        # Coletar filtros
        nome = self.nome.text().strip() if self.nome.text() else None
        descricao = self.descricao.text().strip() if self.descricao.text() else None
        ano_inicio = self.anoInicio.value() if self.anoInicio.value() != self.anoInicio.minimum() else None
        ano_fim = self.anoFim.value() if self.anoFim.value() != self.anoFim.minimum() else None
        
        try:
            # Buscar com filtros
            resultados = buscar_series_filtros(nome, descricao, ano_inicio, ano_fim)
            self.preencher_tabela(resultados)
            
            if not resultados:
                QMessageBox.information(self, "Busca", "Nenhuma série encontrada com os filtros especificados.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro na busca: {str(e)}")

    def preencher_tabela(self, series):
        """Preencher tabela com resultados"""
        self.tabelaResultados.setRowCount(len(series))
        
        for row, serie in enumerate(series):
            # serie = (id, nome, descricao, data_inicio, data_fim)
            self.tabelaResultados.setItem(row, 0, QTableWidgetItem(str(serie[0])))
            self.tabelaResultados.setItem(row, 1, QTableWidgetItem(str(serie[1])))
            self.tabelaResultados.setItem(row, 2, QTableWidgetItem(str(serie[3]) if serie[3] else ""))
            self.tabelaResultados.setItem(row, 3, QTableWidgetItem(str(serie[4]) if serie[4] else ""))

    def limpar(self):
        """Limpar filtros e recarregar todas as séries"""
        self.nome.clear()
        self.descricao.clear()
        self.anoInicio.setValue(self.anoInicio.minimum())
        self.anoFim.setValue(self.anoFim.minimum())
        self.carregar_todas_series()

    def on_selection_changed(self):
        """Habilitar/desabilitar botão Abrir baseado na seleção"""
        tem_selecao = len(self.tabelaResultados.selectedItems()) > 0
        self.btnAbrir.setEnabled(tem_selecao)

    def abrir_serie_selecionada(self):
        """Abrir detalhes da série selecionada"""
        current_row = self.tabelaResultados.currentRow()
        if current_row >= 0:
            serie_id = int(self.tabelaResultados.item(current_row, 0).text())
            
            # Importar e abrir diálogo de detalhes da série
            try:
                # Armazenar ID selecionado e aceitar diálogo para que o chamador saiba
                self.selected_serie_id = serie_id
                self.accept()
                return serie_id
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir série: {str(e)}")
        
        return None
