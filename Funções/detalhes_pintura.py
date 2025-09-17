# -*- coding: utf-8 -*-
"""
Módulo para buscar detalhes completos de pinturas
Separado para evitar importação circular entre Main.py e UI_Dialogs
"""

def mostrar_detalhes(pintura_id, db_path):
    """
    Buscar todos os detalhes de uma pintura incluindo:
    - Dados principais (título, técnica, tamanho, data, local)
    - Fotos da pintura
    - Exposições onde foi exibida
    - Histórico de locais
    - Histórico de preços
    - Preço atual
    - Local atual
    - Caminho das fotos
    
    Args:
        pintura_id: ID da pintura
        db_path: Caminho para o banco de dados
        
    Returns:
        dict: Dicionário com todos os detalhes da pintura
    """
    from pathlib import Path
    
    # Converter para int se necessário
    if isinstance(pintura_id, str):
        pintura_id = int(pintura_id)
    
    BASE_DIR = Path(__file__).parent.parent.resolve()
    
    # 1) Dados principais da pintura
    from Funções.crud_pint import buscar_pintura
    p = buscar_pintura(pintura_id, db_path=str(db_path))
    # p = (id, titulo, tecnica, tamanho, data, local)

    # 2) Fotos da pintura
    from Funções.crud_fotos import listar_fotos
    fotos = listar_fotos(pintura_id, db_path=str(db_path))

    # 3) Exposições onde a pintura foi exibida
    from Funções.crud_pinturas_exposicoes import listar_exposicoes_pintura
    expos = listar_exposicoes_pintura(pintura_id, db_path=str(db_path))

    # 4) Locais onde a pintura esteve
    from Funções.crud_locais import listar_locais_pintura
    locais = listar_locais_pintura(pintura_id, db_path=str(db_path))

    # 5) Histórico de preços da pintura
    from Funções.crud_precos import listar_precos_pintura
    precos = listar_precos_pintura(pintura_id, db_path=str(db_path))

    # 6) Preço atual da pintura
    from Funções.crud_precos import buscar_preco_atual
    preco_atual = buscar_preco_atual(pintura_id, db_path=str(db_path))

    # 7) Local atual da pintura
    from Funções.crud_locais import buscar_local_atual
    local_atual = buscar_local_atual(pintura_id, db_path=str(db_path))

    # 8) Endereço base das fotos (usando gerenciador de pastas)
    from Funções.gerenciador_pastas import gerenciador_pastas
    try:
        # Buscar informações da pintura para obter o título
        if p and len(p) > 1:
            titulo_pintura = p[1]  # Título da pintura
            fotos_path = gerenciador_pastas.obter_pasta_pintura(pintura_id, titulo_pintura)
        else:
            fotos_path = None
    except Exception as e:
        print(f"Erro ao obter pasta da pintura: {e}")
        fotos_path = str(BASE_DIR / "Bibliotecas" / "Pinturas" / f"{pintura_id:04d}_Sem_Nome")

    # Criar dicionário com todos os detalhes
    detalhes_pintura = {   
        "pintura": p,
        "fotos": fotos,
        "exposicoes": expos,
        "locais": locais,
        "precos": precos,
        "preco_atual": preco_atual,
        "local_atual": local_atual,
        "fotos_path": fotos_path
    }

    # Retornar o dicionário completo
    return detalhes_pintura
