# -*- coding: utf-8 -*-
"""
Módulo CRUD para Séries
Operações de banco de dados para gerenciamento de séries de pinturas
"""

import sqlite3 as sql
from pathlib import Path

def listar_series(db_path=None):
    """Listar todas as séries"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    # Garantir que o caminho é uma string e que o diretório existe
    db_path = str(db_path)
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Verificar se o arquivo de banco existe
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Banco de dados não encontrado: {db_path}")
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.id, s.nome, s.descricao, s.data_inicio, s.data_fim,
                   COUNT(ps.pintura_id) as total_pinturas
            FROM series s
            LEFT JOIN pintura_serie ps ON s.id = ps.serie_id
            GROUP BY s.id, s.nome, s.descricao, s.data_inicio, s.data_fim
            ORDER BY s.nome
        """)
        series = cursor.fetchall()
        return series
    except Exception as e:
        print(f"Erro ao listar séries: {e}")
        return []
    finally:
        conn.close()


def buscar_series_filtros(nome=None, descricao=None, ano_inicio=None, ano_fim=None, db_path=None):
    """Buscar séries com filtros específicos"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT s.id, s.nome, s.descricao, s.data_inicio, s.data_fim,
                   COUNT(ps.pintura_id) as total_pinturas
            FROM series s
            LEFT JOIN pintura_serie ps ON s.id = ps.serie_id
            WHERE 1=1
        """
        params = []
        
        if nome:
            query += " AND s.nome LIKE ?"
            params.append(f"%{nome}%")
        
        if descricao:
            query += " AND s.descricao LIKE ?"
            params.append(f"%{descricao}%")
        
        if ano_inicio:
            query += " AND s.data_inicio >= ?"
            params.append(str(ano_inicio))
        
        if ano_fim:
            query += " AND s.data_fim <= ?"
            params.append(str(ano_fim))
        
        query += """
            GROUP BY s.id, s.nome, s.descricao, s.data_inicio, s.data_fim
            ORDER BY s.nome
        """
        
        cursor.execute(query, params)
        series = cursor.fetchall()
        return series
    except Exception as e:
        print(f"Erro ao buscar séries: {e}")
        return []
    finally:
        conn.close()

def adicionar_serie(nome, descricao="", ano_inicio="", ano_fim="", db_path=None):
    """Adicionar uma nova série"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO series (nome, descricao, data_inicio, data_fim)
            VALUES (?, ?, ?, ?)
        """, (nome, descricao, ano_inicio, ano_fim))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao adicionar série: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def buscar_serie(serie_id, db_path=None):
    """Buscar uma série específica por ID"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.id, s.nome, s.descricao, s.data_inicio, s.data_fim,
                   COUNT(ps.pintura_id) as total_pinturas
            FROM series s
            LEFT JOIN pintura_serie ps ON s.id = ps.serie_id
            WHERE s.id = ?
            GROUP BY s.id, s.nome, s.descricao, s.data_inicio, s.data_fim
        """, (serie_id,))
        serie = cursor.fetchone()
        return serie
    except Exception as e:
        print(f"Erro ao buscar série: {e}")
        return None
    finally:
        conn.close()

def atualizar_serie(serie_id, nome, descricao="", ano_inicio="", ano_fim="", db_path=None):
    """Atualizar dados de uma série"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE series 
            SET nome = ?, descricao = ?, data_inicio = ?, data_fim = ?
            WHERE id = ?
        """, (nome, descricao, ano_inicio, ano_fim, serie_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar série: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def remover_serie(serie_id, db_path=None):
    """Remover uma série (apenas se não tiver pinturas associadas)"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se há pinturas associadas através da tabela pintura_serie
        cursor.execute("SELECT COUNT(*) FROM pintura_serie WHERE serie_id = ?", (serie_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, f"Não é possível excluir a série. Há {count} pinturas associadas."
        
        cursor.execute("DELETE FROM series WHERE id = ?", (serie_id,))
        conn.commit()
        return True, "Série removida com sucesso!"
    except Exception as e:
        print(f"Erro ao remover série: {e}")
        conn.rollback()
        return False, f"Erro ao remover série: {e}"
    finally:
        conn.close()

def listar_pinturas_da_serie(serie_id, db_path=None):
    """Listar todas as pinturas de uma série específica"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.id, p.titulo, p.tecnica, p.tamanho, p.data, p.local
            FROM pinturas p
            INNER JOIN pintura_serie ps ON p.id = ps.pintura_id
            WHERE ps.serie_id = ?
            ORDER BY p.titulo
        """, (serie_id,))
        pinturas = cursor.fetchall()
        return pinturas
    except Exception as e:
        print(f"Erro ao listar pinturas da série: {e}")
        return []
    finally:
        conn.close()

def associar_pintura_serie(pintura_id, serie_id, db_path=None):
    """Associar uma pintura a uma série"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se associação já existe
        cursor.execute("""
            SELECT 1 FROM pintura_serie 
            WHERE pintura_id = ? AND serie_id = ?
        """, (pintura_id, serie_id))
        
        if cursor.fetchone():
            return False  # Já existe
        
        # Inserir nova associação
        cursor.execute("""
            INSERT INTO pintura_serie (pintura_id, serie_id)
            VALUES (?, ?)
        """, (pintura_id, serie_id))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Erro ao associar pintura à série: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def remover_pintura_de_serie(pintura_id, serie_id, db_path=None):
    """Remover associação entre pintura e série"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "Data" / "Data.db"
    
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM pintura_serie 
            WHERE pintura_id = ? AND serie_id = ?
        """, (pintura_id, serie_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Erro ao remover pintura da série: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
