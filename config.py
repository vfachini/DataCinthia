# -*- coding: utf-8 -*-
"""
Sistema de Configurações do Aplicativo
Gerencia configurações globais e preferências do usuário
"""

import os
import json
from pathlib import Path

class ConfigManager:
    """Gerenciador de configurações do aplicativo"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "config.json"
        self.default_config = {
            "biblioteca_path": str(Path(__file__).parent / "Bibliotecas"),
            "database_path": str(Path(__file__).parent / "Data" / "Data.db"),
            "backup_enabled": True,
            "auto_create_folders": True,
            "window_size": {"width": 1200, "height": 800},
            "window_maximized": False,
            "theme": "default",
            "language": "pt_BR"
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Carregar configurações do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Mesclar com configurações padrão para garantir integridade
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """Salvar configurações no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def get(self, key, default=None):
        """Obter valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Definir valor de configuração"""
        self.config[key] = value
        self.save_config()
    
    def get_biblioteca_path(self):
        """Obter caminho da biblioteca"""
        return Path(self.config["biblioteca_path"])
    
    def set_biblioteca_path(self, path):
        """Definir caminho da biblioteca"""
        self.config["biblioteca_path"] = str(path)
        self.save_config()
    
    def get_database_path(self):
        """Obter caminho do banco de dados"""
        return Path(self.config["database_path"])
    
    def reset_to_defaults(self):
        """Resetar para configurações padrão"""
        self.config = self.default_config.copy()
        self.save_config()

# Instância global do gerenciador de configurações
config_manager = ConfigManager()
