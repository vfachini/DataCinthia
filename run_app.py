#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher do Gerenciador de Pinturas
Executa a aplicação completa com configurações dinâmicas
"""

import sys
import os
sys.path.append('.')

from Main import MainWindow
from PyQt5.QtWidgets import QApplication
from config import config_manager

def main():
    """Executar aplicação principal"""
    print("🎨 GERENCIADOR DE PINTURAS v2.0")
    print("=" * 40)
    print("🚀 Iniciando aplicação completa...")
    
    # Criar aplicação
    app = QApplication(sys.argv)
    
    # Carregar configurações de janela
    window_config = config_manager.get("window_size", {"width": 1200, "height": 800})
    maximized = config_manager.get("window_maximized", False)
    
    # Criar janela principal
    window = MainWindow()
    window.setWindowTitle("Gerenciador de Pinturas - Sistema Completo v2.0")
    
    # Aplicar configurações de janela
    if not maximized:
        window.resize(window_config["width"], window_config["height"])
    
    # Mostrar janela
    if maximized:
        window.showMaximized()
    else:
        window.show()
    
    print("✅ Aplicação iniciada com sucesso!")
    print("📱 Janela principal visível")
    print(f"� Biblioteca: {config_manager.get_biblioteca_path()}")
    print("🔗 Funcionalidades disponíveis:")
    print("   - Busca de Pinturas ✅")
    print("   - Busca de Exposições ✅") 
    print("   - Busca de Séries ✅")
    print("   - Gestão Visual de Fotos ✅")
    print("   - Edição de Exposições ✅")
    print("   - Edição de Séries ✅")
    print("   - Sistema de Configurações ✅")
    print("   - Painéis de detalhes conectados ✅")
    
    # Executar aplicação
    print("\n💡 Para fechar: Ctrl+C ou feche a janela")
    print("⚙️ Acesse Configurações > Preferências para personalizar")
    
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main()
