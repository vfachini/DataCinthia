# -*- coding: utf-8 -*-
"""
Diálogo de Configurações
Interface para gerenciar configurações do aplicativo
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QGroupBox, QLabel, QPushButton, QLineEdit, 
                            QCheckBox, QSpinBox, QComboBox, QFileDialog,
                            QDialogButtonBox, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from config import config_manager

class ConfigDialog(QDialog):
    """Diálogo principal de configurações"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Sistema")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        """Configurar interface do diálogo"""
        layout = QVBoxLayout(self)
        
        # Criar abas
        self.tab_widget = QTabWidget()
        
        # Aba Geral
        self.tab_geral = self.create_tab_geral()
        self.tab_widget.addTab(self.tab_geral, "Geral")
        
        # Aba Caminhos
        self.tab_caminhos = self.create_tab_caminhos()
        self.tab_widget.addTab(self.tab_caminhos, "Caminhos")
        
        # Aba Interface
        self.tab_interface = self.create_tab_interface()
        self.tab_widget.addTab(self.tab_interface, "Interface")
        
        layout.addWidget(self.tab_widget)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        buttons.accepted.connect(self.accept_changes)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(buttons)
    
    def create_tab_geral(self):
        """Criar aba de configurações gerais"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo Backup
        backup_group = QGroupBox("Backup e Segurança")
        backup_layout = QFormLayout(backup_group)
        
        self.backup_enabled = QCheckBox("Habilitar backup automático")
        backup_layout.addRow("Backup:", self.backup_enabled)
        
        self.auto_create_folders = QCheckBox("Criar pastas automaticamente")
        backup_layout.addRow("Pastas:", self.auto_create_folders)
        
        layout.addWidget(backup_group)
        
        # Grupo Performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.max_recent_files = QSpinBox()
        self.max_recent_files.setRange(5, 50)
        self.max_recent_files.setValue(10)
        performance_layout.addRow("Arquivos recentes:", self.max_recent_files)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
        return widget
    
    def create_tab_caminhos(self):
        """Criar aba de configurações de caminhos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo Biblioteca
        biblioteca_group = QGroupBox("Localização da Biblioteca")
        biblioteca_layout = QVBoxLayout(biblioteca_group)
        
        # Caminho da biblioteca
        biblioteca_row = QHBoxLayout()
        self.biblioteca_path = QLineEdit()
        self.biblioteca_path.setReadOnly(True)
        
        self.btn_escolher_biblioteca = QPushButton("Escolher Pasta...")
        self.btn_escolher_biblioteca.clicked.connect(self.escolher_biblioteca)
        
        biblioteca_row.addWidget(QLabel("Pasta da Biblioteca:"))
        biblioteca_row.addWidget(self.biblioteca_path)
        biblioteca_row.addWidget(self.btn_escolher_biblioteca)
        
        biblioteca_layout.addLayout(biblioteca_row)
        
        # Botão para abrir pasta
        self.btn_abrir_biblioteca = QPushButton("Abrir Pasta da Biblioteca")
        self.btn_abrir_biblioteca.clicked.connect(self.abrir_biblioteca)
        biblioteca_layout.addWidget(self.btn_abrir_biblioteca)
        
        layout.addWidget(biblioteca_group)
        
        # Grupo Banco de Dados
        db_group = QGroupBox("Banco de Dados")
        db_layout = QVBoxLayout(db_group)
        
        db_row = QHBoxLayout()
        self.database_path = QLineEdit()
        self.database_path.setReadOnly(True)
        
        self.btn_escolher_db = QPushButton("Escolher...")
        self.btn_escolher_db.clicked.connect(self.escolher_database)
        
        db_row.addWidget(QLabel("Arquivo do Banco:"))
        db_row.addWidget(self.database_path)
        db_row.addWidget(self.btn_escolher_db)
        
        db_layout.addLayout(db_row)
        layout.addWidget(db_group)
        
        layout.addStretch()
        return widget
    
    def create_tab_interface(self):
        """Criar aba de configurações de interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo Aparência
        aparencia_group = QGroupBox("Aparência")
        aparencia_layout = QFormLayout(aparencia_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Escuro", "Claro"])
        aparencia_layout.addRow("Tema:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português (BR)", "English"])
        aparencia_layout.addRow("Idioma:", self.language_combo)
        
        layout.addWidget(aparencia_group)
        
        # Grupo Janela
        window_group = QGroupBox("Janela")
        window_layout = QFormLayout(window_group)
        
        self.window_maximized = QCheckBox("Iniciar maximizada")
        window_layout.addRow("Inicialização:", self.window_maximized)
        
        self.window_width = QSpinBox()
        self.window_width.setRange(800, 2000)
        window_layout.addRow("Largura padrão:", self.window_width)
        
        self.window_height = QSpinBox()
        self.window_height.setRange(600, 1500)
        window_layout.addRow("Altura padrão:", self.window_height)
        
        layout.addWidget(window_group)
        
        layout.addStretch()
        return widget
    
    def escolher_biblioteca(self):
        """Escolher pasta da biblioteca"""
        pasta = QFileDialog.getExistingDirectory(
            self, 
            "Escolher Pasta da Biblioteca",
            str(config_manager.get_biblioteca_path())
        )
        
        if pasta:
            self.biblioteca_path.setText(pasta)
    
    def abrir_biblioteca(self):
        """Abrir pasta da biblioteca no explorador"""
        import subprocess
        import platform
        
        path = self.biblioteca_path.text() or str(config_manager.get_biblioteca_path())
        
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir a pasta:\n{e}")
    
    def escolher_database(self):
        """Escolher arquivo do banco de dados"""
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Escolher Banco de Dados",
            str(config_manager.get_database_path()),
            "Arquivos SQLite (*.db);;Todos os arquivos (*)"
        )
        
        if arquivo:
            self.database_path.setText(arquivo)
    
    def load_current_config(self):
        """Carregar configurações atuais nos campos"""
        # Aba Geral
        self.backup_enabled.setChecked(config_manager.get("backup_enabled", True))
        self.auto_create_folders.setChecked(config_manager.get("auto_create_folders", True))
        
        # Aba Caminhos
        self.biblioteca_path.setText(str(config_manager.get_biblioteca_path()))
        self.database_path.setText(str(config_manager.get_database_path()))
        
        # Aba Interface
        theme = config_manager.get("theme", "default")
        theme_index = {"default": 0, "dark": 1, "light": 2}.get(theme, 0)
        self.theme_combo.setCurrentIndex(theme_index)
        
        language = config_manager.get("language", "pt_BR")
        lang_index = {"pt_BR": 0, "en": 1}.get(language, 0)
        self.language_combo.setCurrentIndex(lang_index)
        
        self.window_maximized.setChecked(config_manager.get("window_maximized", False))
        
        window_size = config_manager.get("window_size", {"width": 1200, "height": 800})
        self.window_width.setValue(window_size["width"])
        self.window_height.setValue(window_size["height"])
    
    def accept_changes(self):
        """Aplicar e salvar as mudanças"""
        try:
            # Salvar configurações gerais
            config_manager.set("backup_enabled", self.backup_enabled.isChecked())
            config_manager.set("auto_create_folders", self.auto_create_folders.isChecked())
            
            # Salvar caminhos
            if self.biblioteca_path.text():
                config_manager.set_biblioteca_path(self.biblioteca_path.text())
            
            if self.database_path.text():
                config_manager.set("database_path", self.database_path.text())
            
            # Salvar interface
            themes = ["default", "dark", "light"]
            config_manager.set("theme", themes[self.theme_combo.currentIndex()])
            
            languages = ["pt_BR", "en"]
            config_manager.set("language", languages[self.language_combo.currentIndex()])
            
            config_manager.set("window_maximized", self.window_maximized.isChecked())
            config_manager.set("window_size", {
                "width": self.window_width.value(),
                "height": self.window_height.value()
            })
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações:\n{e}")
    
    def restore_defaults(self):
        """Restaurar configurações padrão"""
        reply = QMessageBox.question(
            self, 
            "Confirmar",
            "Tem certeza que deseja restaurar as configurações padrão?\nTodas as configurações atuais serão perdidas.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            config_manager.reset_to_defaults()
            self.load_current_config()
            QMessageBox.information(self, "Sucesso", "Configurações restauradas para os valores padrão!")


# Widget necessário para o create_tab_geral
from PyQt5.QtWidgets import QWidget
