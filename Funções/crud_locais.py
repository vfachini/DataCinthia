# -*- coding: utf-8 -*-
"""
Módulo CRUD para Locais
Operações de banco de dados para gerenciamento de locais das pinturas
"""

import sqlite3 as sql


def adicionar_local(pintura_id, local, data_entrada, data_saida=None, observacao=None, db_path=None):
    """Adiciona um local onde a pintura esteve"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se tabela locais existe, se não, criar
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pintura_id INTEGER,
        local TEXT NOT NULL,
        data_entrada TEXT NOT NULL,
        data_saida TEXT,
        observacao TEXT,
        atual BOOLEAN DEFAULT 0,
        FOREIGN KEY (pintura_id) REFERENCES pinturas(id)
    )
    """)
    
    # Se não tem data_saida, é o local atual
    atual = 1 if data_saida is None else 0
    
    # Se for local atual, desativar outros locais atuais
    if atual:
        cursor.execute("""
        UPDATE locais 
        SET atual = 0 
        WHERE pintura_id = ?
        """, (pintura_id,))
    
    cursor.execute("""
    INSERT INTO locais (pintura_id, local, data_entrada, data_saida, observacao, atual)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (pintura_id, local, data_entrada, data_saida, observacao, atual))
    
    conn.commit()
    conn.close()


def atualizar_local_atual(pintura_id, novo_local, data_saida_anterior, data_entrada_novo, observacao=None, db_path=None):
    """Atualiza o local atual da pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    # Finalizar local atual (adicionar data_saida)
    cursor.execute("""
    UPDATE locais 
    SET data_saida = ?, atual = 0 
    WHERE pintura_id = ? AND atual = 1
    """, (data_saida_anterior, pintura_id))
    
    # Adicionar novo local atual
    cursor.execute("""
    INSERT INTO locais (pintura_id, local, data_entrada, observacao, atual)
    VALUES (?, ?, ?, ?, 1)
    """, (pintura_id, novo_local, data_entrada_novo, observacao))
    
    conn.commit()
    conn.close()


def buscar_local_atual(pintura_id, db_path=None):
    """Busca o local atual de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT local, data_entrada, observacoes
    FROM locais 
    WHERE pintura_id = ?
    ORDER BY data_entrada DESC
    LIMIT 1
    """, (pintura_id,))
    
    local = cursor.fetchone()
    conn.close()
    return local


def listar_locais_pintura(pintura_id, db_path=None):
    """Lista todo o histórico de locais de uma pintura"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, local, data_entrada, data_saida, observacoes
    FROM locais 
    WHERE pintura_id = ? 
    ORDER BY data_entrada DESC
    """, (pintura_id,))
    
    locais = cursor.fetchall()
    conn.close()
    return locais


def historico_localizacao(pintura_id, data_inicio=None, data_fim=None, db_path=None):
    """Busca histórico de localização por período"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT local, data_entrada, data_saida, observacao 
    FROM locais 
    WHERE pintura_id = ?
    """
    params = [pintura_id]
    
    if data_inicio:
        query += " AND data_entrada >= ?"
        params.append(data_inicio)
    
    if data_fim:
        query += " AND (data_saida <= ? OR data_saida IS NULL)"
        params.append(data_fim)
    
    query += " ORDER BY data_entrada DESC"
    
    cursor.execute(query, params)
    locais = cursor.fetchall()
    conn.close()
    return locais


def pinturas_por_local(local, apenas_atuais=False, db_path=None):
    """Lista pinturas que estão ou estiveram em um local específico"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT p.id, p.título, l.data_entrada, l.data_saida, l.atual 
    FROM pinturas p
    JOIN locais l ON p.id = l.pintura_id
    WHERE l.local LIKE ?
    """
    params = [f"%{local}%"]
    
    if apenas_atuais:
        query += " AND l.atual = 1"
    
    query += " ORDER BY l.data_entrada DESC"
    
    cursor.execute(query, params)
    pinturas = cursor.fetchall()
    conn.close()
    return pinturas


def remover_local(local_id, db_path=None):
    """Remove um registro de local"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM locais WHERE id = ?", (local_id,))
    
    conn.commit()
    conn.close()


def listar_todos_locais(db_path=None):
    """Lista todos os locais únicos no sistema"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT DISTINCT local, COUNT(*) as total_pinturas
    FROM locais 
    GROUP BY local 
    ORDER BY local
    """)
    
    locais = cursor.fetchall()
    conn.close()
    return locais


def tempo_no_local(pintura_id, local_id, db_path=None):
    """Calcula quanto tempo uma pintura ficou em um local específico"""
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT data_entrada, data_saida, local 
    FROM locais 
    WHERE id = ? AND pintura_id = ?
    """, (local_id, pintura_id))
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        from datetime import datetime
        data_entrada = datetime.strptime(resultado[0], "%Y-%m-%d")
        
        if resultado[1]:  # tem data_saida
            data_saida = datetime.strptime(resultado[1], "%Y-%m-%d")
        else:  # ainda está lá
            data_saida = datetime.now()
        
        dias = (data_saida - data_entrada).days
        return {
            "local": resultado[2],
            "data_entrada": resultado[0],
            "data_saida": resultado[1],
            "dias_no_local": dias
        }
    
    return None
