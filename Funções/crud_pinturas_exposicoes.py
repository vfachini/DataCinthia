# -*- coding: utf-8 -*-
"""
Módulo CRUD para Pinturas-Exposições
Operações de banco de dados para gerenciamento de relacionamentos entre pinturas e exposições
"""

import sqlite3 as sql


def associar_pintura_exposicao(pintura_id, exposicao_id, db_path=None):
    """Adiciona uma pintura a uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se já existe
        cursor.execute("""
            SELECT COUNT(*) FROM pintura_exposicao 
            WHERE pintura_id = ? AND exposicao_id = ?
        """, (pintura_id, exposicao_id))
        
        if cursor.fetchone()[0] > 0:
            return False  # Já existe
        
        cursor.execute("""
        INSERT INTO pintura_exposicao (pintura_id, exposicao_id)
        VALUES (?, ?)
        """, (pintura_id, exposicao_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao associar pintura à exposição: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def remover_pintura_exposicao(pintura_id, exposicao_id, db_path=None):
    """Remove uma pintura de uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        DELETE FROM pintura_exposicao
        WHERE pintura_id = ? AND exposicao_id = ?
        """, (pintura_id, exposicao_id))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao remover pintura da exposição: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def listar_pinturas_exposicao(exposicao_id, db_path=None):
    """Lista todas as pinturas de uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        SELECT p.id, p.titulo, p.tecnica, p.tamanho, p.data
        FROM pinturas p
        JOIN pintura_exposicao pe ON p.id = pe.pintura_id
        WHERE pe.exposicao_id = ?
        ORDER BY p.titulo
        """, (exposicao_id,))

        pinturas = cursor.fetchall()
        return pinturas
    except Exception as e:
        print(f"Erro ao listar pinturas da exposição: {e}")
        return []
    finally:
        conn.close()


def listar_por_pintura(pintura_id, db_path=None):
    """Lista todas as exposições de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT exposições.*
    FROM exposições
    JOIN pintura_exposição ON exposições.id = pintura_exposição.exposicao_id
    WHERE pintura_exposição.pintura_id = ?
    """, (pintura_id,))

    exposicoes = cursor.fetchall()
    conn.close()
    return exposicoes


def mostrar_detalhes_exposicao(exposicao_id, db_path):
    """Retorna detalhes completos de uma exposição com suas obras"""
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    # Buscar dados da exposição
    cursor.execute("SELECT * FROM exposições WHERE id = ?", (exposicao_id,))
    exposicao = cursor.fetchone()
    
    if not exposicao:
        conn.close()
        return None
    
    # Buscar obras relacionadas à exposição
    cursor.execute("""
        SELECT p.id, p.título 
        FROM pinturas p 
        JOIN pintura_exposição pe ON p.id = pe.pintura_id 
        WHERE pe.exposicao_id = ?
    """, (exposicao_id,))
    obras = cursor.fetchall()
    
    conn.close()
    
    return {
        "exposicao": exposicao,
        "obras": obras
    }


def listar_obras_exposicao(exposicao_id, db_path):
    """Lista todas as obras de uma exposição específica com detalhes"""
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.id, p.título, p.técnica, p.tamanho, p.data
        FROM pinturas p 
        JOIN pintura_exposição pe ON p.id = pe.pintura_id 
        WHERE pe.exposicao_id = ?
    """, (exposicao_id,))
    obras = cursor.fetchall()
    
    conn.close()
    return obras


def listar_exposicoes_pintura(pintura_id, db_path=None):
    """Lista todas as exposições onde uma pintura específica foi exibida"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.id, e.nome, e.data, e.local
        FROM exposicoes e
        JOIN pintura_exposicao pe ON e.id = pe.exposicao_id
        WHERE pe.pintura_id = ?
    """, (pintura_id,))
    exposicoes = cursor.fetchall()
    
    conn.close()
    return exposicoes


def contar_obras_exposicao(exposicao_id, db_path=None):
    """Conta quantas obras tem uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pintura_exposição 
        WHERE exposicao_id = ?
    """, (exposicao_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count


def verificar_pintura_em_exposicao(pintura_id, exposicao_id, db_path=None):
    """Verifica se uma pintura já está em uma exposição"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pintura_exposição 
        WHERE pintura_id = ? AND exposicao_id = ?
    """, (pintura_id, exposicao_id))
    
    existe = cursor.fetchone()[0] > 0
    conn.close()
    return existe
