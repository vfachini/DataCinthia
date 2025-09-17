# -*- coding: utf-8 -*-
"""
Módulo CRUD para Pinturas
Operações de banco de dados para gerenciamento de pinturas
"""

import sqlite3 as sql 


def adicionar_pintura(titulo, tecnica, tamanho, data, local, serie_id=None, exposicao_id=None, preco=None, db_path=None):
    """Adicionar pintura com relacionamentos opcionais"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Inserir pintura principal
        cursor.execute("""
        INSERT INTO pinturas (titulo, tecnica, tamanho, data, local)
        VALUES (?, ?, ?, ?, ?)
        """, (titulo, tecnica, tamanho, data, local))
        
        pintura_id = cursor.lastrowid
        
        # Criar pasta automática para a pintura
        try:
            from .gerenciador_pastas import gerenciador_pastas
            pasta_criada = gerenciador_pastas.criar_pasta_pintura(pintura_id, titulo)
            print(f"Pasta criada para pintura: {pasta_criada}")
        except Exception as e:
            print(f"Erro ao criar pasta (nao critico): {e}")
        
        # Adicionar à série se especificado
        if serie_id:
            cursor.execute("""
            INSERT INTO pintura_serie (pintura_id, serie_id)
            VALUES (?, ?)
            """, (pintura_id, serie_id))
        
        # Adicionar à exposição se especificado
        if exposicao_id:
            cursor.execute("""
            INSERT INTO pintura_exposicao (pintura_id, exposicao_id)
            VALUES (?, ?)
            """, (pintura_id, exposicao_id))
        
        # Adicionar preço se especificado
        if preco:
            from datetime import datetime
            data_preco = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
            INSERT INTO precos (pintura_id, valor, data_avaliacao)
            VALUES (?, ?, ?)
            """, (pintura_id, preco, data_preco))
        
        conn.commit()
        print("Pintura adicionada com sucesso!")
        return pintura_id
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar pintura: {e}")
        raise e
    finally:
        conn.close()


def listar_pinturas(db_path=None):
    """Listar todas as pinturas"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pinturas")
    pinturas = cursor.fetchall()
    
    conn.close()
    return pinturas

def buscar_pintura(pintura_id, db_path=None):
    """Buscar uma pintura específica por ID"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pinturas WHERE id = ?", (pintura_id,))
    pintura = cursor.fetchone()
    
    conn.close()
    return pintura

def atualizar_pintura(pintura_id, titulo, tecnica, tamanho, data, local, preco=None):
    """Atualizar pintura existente"""
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        UPDATE pinturas
        SET titulo = ?, tecnica = ?, tamanho = ?, data = ?, local = ?
        WHERE id = ?
        """, (titulo, tecnica, tamanho, data, local, pintura_id))
        
        conn.commit()
        print("Pintura atualizada com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao atualizar pintura: {e}")
        return False
    finally:
        conn.close()

def remover_pintura(pintura_id):
    """Remover pintura do banco de dados"""
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM pinturas WHERE id = ?", (pintura_id,))
        
        conn.commit()
        print(f"Pintura {pintura_id} removida com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao remover pintura: {e}")
        return False
    finally:
        conn.close()

def busca_filtros(titulo=None, tecnica=None, tamanho=None, data=None, local=None):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    query = "SELECT * FROM pinturas WHERE 1=1"
    params = []
    
    if titulo:
        query += " AND titulo LIKE ?"
        params.append(f"%{titulo}%")
    if tecnica:
        query += " AND tecnica LIKE ?"
        params.append(f"%{tecnica}%")
    if tamanho:
        query += " AND tamanho LIKE ?"
        params.append(f"%{tamanho}%")
    if data:
        query += " AND data LIKE ?"
        params.append(f"%{data}%")
    if local:
        query += " AND local LIKE ?"
        params.append(f"%{local}%")
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    conn.close()
    return resultados

def busca_avancada(titulo=None, tecnica=None, tamanho=None, data=None, local=None, 
                   preco_min=None, preco_max=None, serie=None, exposicao=None):
    """
    Busca avançada com filtros por preço, série e exposição
    """
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    # Query base com JOINs para incluir informações relacionadas
    query = """
    SELECT DISTINCT p.id, p.titulo, p.tecnica, p.tamanho, p.data, p.local, p.serie_id,
           pr.valor as preco_atual, s.nome as serie_nome, 
           GROUP_CONCAT(e.nome) as exposicoes
    FROM pinturas p
    LEFT JOIN (
        SELECT pintura_id, valor, 
               ROW_NUMBER() OVER (PARTITION BY pintura_id ORDER BY data_avaliacao DESC) as rn
        FROM precos
    ) pr ON p.id = pr.pintura_id AND pr.rn = 1
    LEFT JOIN series s ON p.serie_id = s.id
    LEFT JOIN pintura_exposicao pe ON p.id = pe.pintura_id
    LEFT JOIN exposicoes e ON pe.exposicao_id = e.id
    WHERE 1=1
    """
    params = []
    
    # Filtros básicos
    if titulo:
        query += " AND p.titulo LIKE ?"
        params.append(f"%{titulo}%")
    if tecnica:
        query += " AND p.tecnica LIKE ?"
        params.append(f"%{tecnica}%")
    if tamanho:
        query += " AND p.tamanho LIKE ?"
        params.append(f"%{tamanho}%")
    if data:
        query += " AND p.data LIKE ?"
        params.append(f"%{data}%")
    if local:
        query += " AND p.local LIKE ?"
        params.append(f"%{local}%")
    
    # Filtros avançados
    if preco_min:
        query += " AND pr.valor >= ?"
        params.append(float(preco_min))
    if preco_max:
        query += " AND pr.valor <= ?"
        params.append(float(preco_max))
    if serie:
        query += " AND s.nome LIKE ?"
        params.append(f"%{serie}%")
    if exposicao:
        query += " AND e.nome LIKE ?"
        params.append(f"%{exposicao}%")
    
    query += " GROUP BY p.id ORDER BY p.titulo"
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    conn.close()
    return resultados