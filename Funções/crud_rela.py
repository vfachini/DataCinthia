import sqlite3 as sql


def adicionar_pintura_exposicao(pintura_id, exposicao_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO pintura_exposição (pintura_id, exposicao_id)
    VALUES (?, ?)
    """, (pintura_id, exposicao_id))
    
    conn.commit()
    conn.close()

def listar_por_exposicao(exposicao_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT pinturas.*
    FROM pinturas
    JOIN pintura_exposição ON pinturas.id = pintura_exposição.pintura_id
    WHERE pintura_exposição.exposicao_id = ?
    """, (exposicao_id,))

    pinturas = cursor.fetchall()
    conn.close()
    return pinturas


def listar_por_pintura(pintura_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
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


def remover_pintura_de_exposicao(pintura_id, exposicao_id):
    conn = sql.connect("C:\\Users\\virtu\\Desktop\\EDU\\Programação\\DB\\Data\\Data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    DELETE FROM pintura_exposição
    WHERE pintura_id = ? AND exposicao_id = ?
    """, (pintura_id, exposicao_id))
    
    conn.commit()
    conn.close()


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
    """Lista todas as obras de uma exposição específica"""
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


def listar_exposicoes_pintura(pintura_id, db_path):
    """Lista todas as exposições onde uma pintura específica foi exibida"""
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.id, e.nome, e.data, e.local
        FROM exposições e
        JOIN pintura_exposição pe ON e.id = pe.exposicao_id
        WHERE pe.pintura_id = ?
    """, (pintura_id,))
    exposicoes = cursor.fetchall()
    
    conn.close()
    return exposicoes
