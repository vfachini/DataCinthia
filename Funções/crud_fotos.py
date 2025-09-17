# -*- coding: utf-8 -*-
"""
Módulo CRUD para Fotos
Operações de banco de dados para gerenciamento de fotos das pinturas
"""

import sqlite3 as sql   


def adicionar_foto(pintura_id, caminho, descricao):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO fotos (pintura_id, caminho, descricao)
    VALUES (?, ?, ?)
    """, (pintura_id, caminho, descricao))
    
    conn.commit()
    conn.close()


def listar_fotos(pintura_id, db_path=None):
    if db_path is None:
        db_path = "C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, caminho, descricao FROM fotos WHERE pintura_id = ?", (pintura_id,))
    fotos = cursor.fetchall()
    conn.close()
    return fotos


def buscar_foto(foto_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM fotos WHERE id = ?", (foto_id,))
    foto = cursor.fetchone()
    
    conn.close()
    return foto 

def remover_foto(foto_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM fotos WHERE id = ?", (foto_id,))
    
    conn.commit()
    conn.close()


def editar_descriçao(foto_id, nova_descricao):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE fotos
    SET descricao = ?
    WHERE id = ?
    """, (nova_descricao, foto_id))
    
    conn.commit()
    conn.close()
