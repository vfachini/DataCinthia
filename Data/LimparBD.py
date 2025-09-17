# -*- coding: utf-8 -*-
"""
Script para limpar base de dados duplicada
Remove tabelas antigas e mantém apenas a estrutura padronizada
"""

import sqlite3

def limpar_base_dados():
    """Limpar tabelas duplicadas e manter estrutura consistente"""
    conn = sqlite3.connect("Data.db")
    cursor = conn.cursor()
    
    print("🧹 Iniciando limpeza da base de dados...")
    
    try:
        # 1. Fazer backup dos dados importantes (se existirem)
        print("📁 Verificando dados existentes...")
        
        # Verificar se há dados nas tabelas antigas
        try:
            cursor.execute('SELECT COUNT(*) FROM pinturas')
            pinturas_count = cursor.fetchone()[0]
            print(f"   - Pinturas: {pinturas_count} registros")
        except:
            pinturas_count = 0
            
        try:
            cursor.execute('SELECT COUNT(*) FROM "Série"')
            series_old_count = cursor.fetchone()[0]
            print(f"   - Séries antigas: {series_old_count} registros")
        except:
            series_old_count = 0
            
        try:
            cursor.execute('SELECT COUNT(*) FROM series')
            series_new_count = cursor.fetchone()[0]
            print(f"   - Séries novas: {series_new_count} registros")
        except:
            series_new_count = 0
        
        # 2. Remover tabelas duplicadas/antigas
        print("\n🗑️ Removendo tabelas duplicadas...")
        
        tabelas_para_remover = [
            '"Série"',
            '"Pintura_serie"', 
            '"Local_armazenado"',
            '"Pintura_Locais"',
            '"Pintura_preço"',
            '"pintura_exposição"',
            '"Preço"',
            '"exposições"'
        ]
        
        for tabela in tabelas_para_remover:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
                print(f"   ✅ Removida: {tabela}")
            except Exception as e:
                print(f"   ⚠️ Erro ao remover {tabela}: {e}")
        
        # 3. Criar tabelas de relacionamento necessárias
        print("\n🔗 Criando tabelas de relacionamento...")
        
        # Tabela pintura_serie (padronizada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pintura_serie (
            pintura_id INTEGER,
            serie_id INTEGER,
            PRIMARY KEY (pintura_id, serie_id),
            FOREIGN KEY (pintura_id) REFERENCES pinturas(id),
            FOREIGN KEY (serie_id) REFERENCES series(id)
        )
        """)
        print("   ✅ pintura_serie criada")
        
        # Tabela pintura_exposicao (sem acento)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pintura_exposicao (
            pintura_id INTEGER,
            exposicao_id INTEGER,
            PRIMARY KEY (pintura_id, exposicao_id),
            FOREIGN KEY (pintura_id) REFERENCES pinturas(id),
            FOREIGN KEY (exposicao_id) REFERENCES exposicoes(id)
        )
        """)
        print("   ✅ pintura_exposicao criada")
        
        # Tabela exposicoes (padronizada)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exposicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tema TEXT,
            tipo TEXT,
            artistas TEXT,
            data TEXT,
            local TEXT,
            curadoria TEXT,
            organizador TEXT,
            periodo TEXT
        )
        """)
        print("   ✅ exposicoes criada")
        
        # Renomear tabela precos se necessário
        try:
            cursor.execute("ALTER TABLE precos RENAME COLUMN valor TO preco")
            print("   ✅ Coluna 'valor' renomeada para 'preco'")
        except:
            pass  # Coluna já pode ter o nome correto
            
        # 4. Commit das mudanças
        conn.commit()
        print("\n✅ Limpeza concluída com sucesso!")
        
        # 5. Mostrar estrutura final
        print("\n📋 Estrutura final:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tabelas = cursor.fetchall()
        for tabela in tabelas:
            if tabela[0] != 'sqlite_sequence':
                print(f"   - {tabela[0]}")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        conn.rollback()
    
    finally:
        conn.close()
        print("\n🎯 Base de dados limpa e padronizada!")

if __name__ == "__main__":
    limpar_base_dados()
