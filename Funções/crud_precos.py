# -*- coding: utf-8 -*-
"""
Módulo CRUD para Preços
Operações de banco de dados para gerenciamento de preços das pinturas
"""

import sqlite3 as sql


def adicionar_preco(pintura_id, preco, data, observacao=None, db_path=None):
    """Adiciona um preço para uma pintura em uma data específica"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se tabela precos existe, se não, criar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pintura_id INTEGER,
        preco REAL NOT NULL,
        data TEXT NOT NULL,
        observacao TEXT,
        ativo BOOLEAN DEFAULT 1,
        FOREIGN KEY (pintura_id) REFERENCES pinturas(id)
    )
    """)
    
    cursor.execute("""
    INSERT INTO precos (pintura_id, preco, data, observacao)
    VALUES (?, ?, ?, ?)
    """, (pintura_id, preco, data, observacao))
    
    conn.commit()
    conn.close()


def atualizar_preco_atual(pintura_id, novo_preco, data, observacao=None, db_path=None):
    """Atualiza o preço atual de uma pintura (desativa o anterior e adiciona novo)"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    # Desativar preço atual
    cursor.execute("""
    UPDATE precos 
    SET ativo = 0 
    WHERE pintura_id = ? AND ativo = 1
    """, (pintura_id,))
    
    # Adicionar novo preço
    cursor.execute("""
    INSERT INTO precos (pintura_id, preco, data, observacao, ativo)
    VALUES (?, ?, ?, ?, 1)
    """, (pintura_id, novo_preco, data, observacao))
    
    conn.commit()
    conn.close()


def buscar_preco_atual(pintura_id, db_path=None):
    """Busca o preço atual (ativo) de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT preco, data, observacoes
    FROM precos 
    WHERE pintura_id = ?
    ORDER BY data DESC 
    LIMIT 1
    """, (pintura_id,))
    
    preco = cursor.fetchone()
    conn.close()
    return preco


def listar_precos_pintura(pintura_id, db_path=None):
    """Lista todo o histórico de preços de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, preco, data, observacoes
    FROM precos 
    WHERE pintura_id = ? 
    ORDER BY data DESC
    """, (pintura_id,))
    
    precos = cursor.fetchall()
    conn.close()
    return precos


def historico_precos(pintura_id, data_inicio=None, data_fim=None, db_path=None):
    """Busca histórico de preços por período"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT preco, data, observacao, ativo 
    FROM precos 
    WHERE pintura_id = ?
    """
    params = [pintura_id]
    
    if data_inicio:
        query += " AND data >= ?"
        params.append(data_inicio)
    
    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim)
    
    query += " ORDER BY data DESC"
    
    cursor.execute(query, params)
    precos = cursor.fetchall()
    conn.close()
    return precos


def remover_preco(preco_id, db_path=None):
    """Remove um registro de preço"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM precos WHERE id = ?", (preco_id,))
    
    conn.commit()
    conn.close()


def listar_pinturas_por_faixa_preco(preco_min, preco_max, db_path=None):
    """Lista pinturas dentro de uma faixa de preço (apenas preços ativos)"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.id, p.título, pr.preco, pr.data 
    FROM pinturas p
    JOIN precos pr ON p.id = pr.pintura_id
    WHERE pr.ativo = 1 AND pr.preco BETWEEN ? AND ?
    ORDER BY pr.preco
    """, (preco_min, preco_max))
    
    pinturas = cursor.fetchall()
    conn.close()
    return pinturas


def estatisticas_precos(pintura_id, db_path=None):
    """Retorna estatísticas de preços de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        MIN(preco) as preco_minimo,
        MAX(preco) as preco_maximo,
        AVG(preco) as preco_medio,
        COUNT(*) as total_alteracoes
    FROM precos 
    WHERE pintura_id = ?
    """, (pintura_id,))
    
    stats = cursor.fetchone()
    conn.close()
    return {
        "preco_minimo": stats[0],
        "preco_maximo": stats[1],
        "preco_medio": stats[2],
        "total_alteracoes": stats[3]
    }
