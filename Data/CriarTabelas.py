# -*- coding: utf-8 -*-
"""
Script de criação de tabelas do banco de dados
Cria a estrutura completa do banco SQLite para o sistema de pinturas
"""

import sqlite3 as sql 


conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")



conn.execute("""
CREATE TABLE IF NOT EXISTS pinturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tecnica TEXT,
    tamanho TEXT,
    data TEXT,
    local TEXT,
    serie_id INTEGER,
    FOREIGN KEY (serie_id) REFERENCES series(id)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    data_inicio TEXT,
    data_fim TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS exposições (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tema TEXT,
    artistas TEXT,
    data TEXT,
    local TEXT,
    curadoria TEXT,
    organizador TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS pintura_exposição (
    pintura_id INTEGER,
    exposicao_id INTEGER,
    PRIMARY KEY (pintura_id, exposicao_id),
    FOREIGN KEY (pintura_id) REFERENCES pinturas(id),
    FOREIGN KEY (exposicao_id) REFERENCES exposições(id)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pintura_id INTEGER,
    caminho TEXT NOT NULL,
    descrição TEXT,
    FOREIGN KEY (pintura_id) REFERENCES pinturas(id)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS precos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pintura_id INTEGER,
    valor REAL,
    data_avaliacao TEXT,
    observacoes TEXT,
    FOREIGN KEY (pintura_id) REFERENCES pinturas(id)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS locais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pintura_id INTEGER,
    local TEXT,
    data_entrada TEXT,
    data_saida TEXT,
    observacoes TEXT,
    FOREIGN KEY (pintura_id) REFERENCES pinturas(id)
)
""")

conn.commit()
conn.close()
print("Tabelas criadas com sucesso!")