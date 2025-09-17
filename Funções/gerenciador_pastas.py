# -*- coding: utf-8 -*-
"""
Módulo de Gerenciamento de Estrutura de Pastas
Cria e organiza automaticamente as pastas para fotos de pinturas e exposições
"""

import os
from pathlib import Path
import shutil
from datetime import datetime

class GerenciadorPastas:
    def __init__(self, pasta_base=None):
        """Inicializar gerenciador de pastas"""
        if pasta_base is None:
            # Tentar usar configuração, senão usar pasta padrão
            try:
                from ..config import config_manager
                self.pasta_base = config_manager.get_biblioteca_path()
            except ImportError:
                # Fallback para pasta padrão se config não estiver disponível
                self.pasta_base = Path(__file__).parent.parent / "Bibliotecas"
        else:
            self.pasta_base = Path(pasta_base)
        
        self._criar_estrutura_base()
    
    def _criar_estrutura_base(self):
        """Criar estrutura básica de pastas"""
        try:
            # Estrutura: Bibliotecas/Exposições e Bibliotecas/Pinturas
            self.pasta_exposicoes = self.pasta_base / "Exposições"
            self.pasta_pinturas = self.pasta_base / "Pinturas"
            
            # Criar pastas se não existirem
            self.pasta_exposicoes.mkdir(parents=True, exist_ok=True)
            self.pasta_pinturas.mkdir(parents=True, exist_ok=True)
            
            print(f"📁 Estrutura de pastas criada em: {self.pasta_base}")
            print(f"   - Exposições: {self.pasta_exposicoes}")
            print(f"   - Pinturas: {self.pasta_pinturas}")
            
        except Exception as e:
            print(f"❌ Erro ao criar estrutura de pastas: {e}")
            raise e
    
    def criar_pasta_pintura(self, pintura_id, titulo_pintura):
        """Criar pasta específica para uma pintura"""
        try:
            # Limpar nome para ser válido como nome de pasta
            nome_limpo = self._limpar_nome_arquivo(titulo_pintura)
            nome_pasta = f"{pintura_id:04d}_{nome_limpo}"
            
            pasta_pintura = self.pasta_pinturas / nome_pasta
            pasta_pintura.mkdir(exist_ok=True)
            
            # Criar apenas uma pasta simples para fotos
            (pasta_pintura / "Fotos").mkdir(exist_ok=True)
            
            print(f"🎨 Pasta criada para pintura: {pasta_pintura}")
            return str(pasta_pintura)
            
        except Exception as e:
            print(f"❌ Erro ao criar pasta para pintura {pintura_id}: {e}")
            return None
    
    def criar_pasta_exposicao(self, exposicao_id, nome_exposicao):
        """Criar pasta específica para uma exposição"""
        try:
            # Limpar nome para ser válido como nome de pasta
            nome_limpo = self._limpar_nome_arquivo(nome_exposicao)
            nome_pasta = f"{exposicao_id:04d}_{nome_limpo}"
            
            pasta_exposicao = self.pasta_exposicoes / nome_pasta
            pasta_exposicao.mkdir(exist_ok=True)
            
            # Criar subpastas organizacionais
            (pasta_exposicao / "Catálogo").mkdir(exist_ok=True)
            (pasta_exposicao / "Fotos_Montagem").mkdir(exist_ok=True)
            (pasta_exposicao / "Documentação").mkdir(exist_ok=True)
            (pasta_exposicao / "Obras_Expostas").mkdir(exist_ok=True)
            
            print(f"🖼️ Pasta criada para exposição: {pasta_exposicao}")
            return str(pasta_exposicao)
            
        except Exception as e:
            print(f"❌ Erro ao criar pasta para exposição {exposicao_id}: {e}")
            return None
    
    def obter_pasta_pintura(self, pintura_id, titulo_pintura=None):
        """Obter caminho da pasta de uma pintura (criar se não existir)"""
        try:
            # Procurar pasta existente
            for pasta in self.pasta_pinturas.iterdir():
                if pasta.is_dir() and pasta.name.startswith(f"{pintura_id:04d}_"):
                    return str(pasta)
            
            # Se não encontrou e tem título, criar nova
            if titulo_pintura:
                return self.criar_pasta_pintura(pintura_id, titulo_pintura)
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter pasta da pintura {pintura_id}: {e}")
            return None
    
    def obter_pasta_exposicao(self, exposicao_id, nome_exposicao=None):
        """Obter caminho da pasta de uma exposição (criar se não existir)"""
        try:
            # Procurar pasta existente
            for pasta in self.pasta_exposicoes.iterdir():
                if pasta.is_dir() and pasta.name.startswith(f"{exposicao_id:04d}_"):
                    return str(pasta)
            
            # Se não encontrou e tem nome, criar nova
            if nome_exposicao:
                return self.criar_pasta_exposicao(exposicao_id, nome_exposicao)
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter pasta da exposição {exposicao_id}: {e}")
            return None
    
    def _limpar_nome_arquivo(self, nome):
        """Limpar nome para ser válido como nome de arquivo/pasta"""
        import re
        # Remover caracteres inválidos para nomes de arquivo
        nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome)
        # Limitar tamanho
        nome_limpo = nome_limpo[:50].strip()
        # Substituir espaços por underscores
        nome_limpo = nome_limpo.replace(' ', '_')
        return nome_limpo
    
    def mover_arquivo_para_pasta(self, arquivo_origem, pasta_destino, subfolder="Fotos"):
        """Mover arquivo para pasta específica"""
        try:
            pasta_destino = Path(pasta_destino)
            pasta_final = pasta_destino / subfolder
            pasta_final.mkdir(exist_ok=True)
            
            arquivo_origem = Path(arquivo_origem)
            arquivo_destino = pasta_final / arquivo_origem.name
            
            # Mover arquivo
            shutil.move(str(arquivo_origem), str(arquivo_destino))
            
            print(f"📂 Arquivo movido: {arquivo_destino}")
            return str(arquivo_destino)
            
        except Exception as e:
            print(f"❌ Erro ao mover arquivo: {e}")
            return None
    
    def listar_pastas_pinturas(self):
        """Listar todas as pastas de pinturas"""
        try:
            pastas = []
            for pasta in self.pasta_pinturas.iterdir():
                if pasta.is_dir():
                    pastas.append({
                        'id': int(pasta.name.split('_')[0]),
                        'nome': pasta.name,
                        'caminho': str(pasta)
                    })
            return sorted(pastas, key=lambda x: x['id'])
        except Exception as e:
            print(f"❌ Erro ao listar pastas de pinturas: {e}")
            return []
    
    def listar_pastas_exposicoes(self):
        """Listar todas as pastas de exposições"""
        try:
            pastas = []
            for pasta in self.pasta_exposicoes.iterdir():
                if pasta.is_dir():
                    pastas.append({
                        'id': int(pasta.name.split('_')[0]),
                        'nome': pasta.name,
                        'caminho': str(pasta)
                    })
            return sorted(pastas, key=lambda x: x['id'])
        except Exception as e:
            print(f"❌ Erro ao listar pastas de exposições: {e}")
            return []

# Instância global para uso em todo o projeto
gerenciador_pastas = GerenciadorPastas()
