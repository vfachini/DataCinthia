# -*- coding: utf-8 -*-
"""
Módulo CRUD para Exposições
Operações de banco de dados para gerenciamento de exposições
"""

import sqlite3 as sql 

def adicionar_exposicao(nome, tema, tipo, artistas, data, local, curadoria, organizador, periodo=None):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO exposicoes (nome, tema, tipo, artistas, data, local, curadoria, organizador, periodo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, tema, tipo, artistas, data, local, curadoria, organizador, periodo))
        
        exposicao_id = cursor.lastrowid
        
        # Criar pasta automática para a exposição
        try:
            from .gerenciador_pastas import gerenciador_pastas
            pasta_criada = gerenciador_pastas.criar_pasta_exposicao(exposicao_id, nome)
            print(f"Pasta criada para exposicao: {pasta_criada}")
        except Exception as e:
            print(f"Erro ao criar pasta (nao critico): {e}")
        
        conn.commit()
        print("Exposição adicionada com sucesso!")
        return exposicao_id
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar exposição: {e}")
        raise e
    finally:
        conn.close()

def listar_exposicoes():
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exposicoes")
    exposicoes = cursor.fetchall()
    
    conn.close()
    return exposicoes   

def buscar_exposicao(exposicao_id, db_path=None): 
    """Buscar uma exposição específica por ID"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM exposicoes WHERE id = ?", (exposicao_id,))
        exposicao = cursor.fetchone()
        return exposicao
    except Exception as e:
        print(f"Erro ao buscar exposição: {e}")
        return None
    finally:
        conn.close()

def atualizar_exposicao(exposicao_id, nome, tema, artistas, data, local, curadoria, organizador, db_path=None):
    """Atualizar dados de uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        UPDATE exposicoes
        SET nome = ?, tema = ?, artistas = ?, data = ?, local = ?, curadoria = ?, organizador = ?
        WHERE id = ?
        """, (nome, tema, artistas, data, local, curadoria, organizador, exposicao_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar exposição: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def remover_exposicao(exposicao_id, db_path=None):
    """Remover uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se há pinturas associadas
        cursor.execute("SELECT COUNT(*) FROM pintura_exposicao WHERE exposicao_id = ?", (exposicao_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, f"Não é possível excluir a exposição. Há {count} obras associadas."
        
        cursor.execute("DELETE FROM exposicoes WHERE id = ?", (exposicao_id,))
        conn.commit()
        return True, "Exposição removida com sucesso!"
        
    except Exception as e:
        print(f"Erro ao remover exposição: {e}")
        conn.rollback()
        return False, f"Erro ao remover exposição: {e}"
    finally:
        conn.close()


def buscar_exposicoes_filtros(nome=None, local=None, ano=None, apenas_ativas=False, db_path=None):
    """Buscar exposições com filtros avançados"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Construir query base com contagem de obras
        query = """
        SELECT e.id, e.nome, e.data, e.local, 
               COALESCE(COUNT(pe.pintura_id), 0) as total_obras
        FROM exposicoes e
        LEFT JOIN pintura_exposicao pe ON e.id = pe.exposicao_id
        WHERE 1=1
        """
        
        params = []
        
        # Adicionar filtros
        if nome:
            query += " AND e.nome LIKE ?"
            params.append(f"%{nome}%")
            
        if local:
            query += " AND e.local LIKE ?"
            params.append(f"%{local}%")
            
        if ano:
            query += " AND e.data LIKE ?"
            params.append(f"%{ano}%")
            
        # Filtro para exposições ativas (com obras)
        if apenas_ativas:
            query += " GROUP BY e.id HAVING total_obras > 0"
        else:
            query += " GROUP BY e.id"
            
        # Ordenar por nome
        query += " ORDER BY e.nome"
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        return resultados
        
    except Exception as e:
        print(f"Erro ao buscar exposições: {e}")
        return []
    finally:
        conn.close()
