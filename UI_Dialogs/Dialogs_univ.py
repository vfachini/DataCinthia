# -*- coding: utf-8 -*-
"""
Diálogos universais
Classes de diálogo comuns e utilitários gerais
"""

from PyQt5.QtWidgets import QDialog, QMainWindow, QVBoxLayout, QDialogButtonBox, QMessageBox
from PyQt5 import uic
import os
import sys
from pathlib import Path  

# Adicionar o diretório pai ao path para importações
sys.path.append(str(Path(__file__).parent.parent))

from Funções.crud_pint import listar_pinturas, busca_filtros, adicionar_pintura, atualizar_pintura, buscar_pintura, remover_pintura

BASE_DIR = Path(__file__).parent.parent.resolve()
UI_DIR   = BASE_DIR / "Interface"
DB_PATH  = BASE_DIR / "Data" / "Data.db"




class Confirmar_exclusão(QDialog):# janela que abre quando o usuário tenta excluir uma ou uma seleção de pintura,exposição ou série
    def __init__(self, item):
        super(Confirmar_exclusão, self).__init__()
        uic.loadUi(os.path.join(UI_DIR, "Deletar", 'confirmar_Del.ui'), self)
        
        self.item = item
        self.label.setText(f"Você tem certeza que deseja excluir {item}?")
        
        self.buttonBox.accepted.connect(self.excluir)
        self.buttonBox.rejected.connect(self.reject)

    def excluir(self):
        remover_pintura(self.item)
        QMessageBox.information(self, "Sucesso", f"{self.item} excluído com sucesso!")
        self.accept()
        