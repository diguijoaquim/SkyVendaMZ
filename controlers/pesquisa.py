from sqlalchemy.orm import Session
from controlers.produto import *
from sqlalchemy import or_
from datetime import datetime
from fastapi import APIRouter,Form,File,Query
from models import Produto,Pesquisa,Usuario,Comentario,produto_likes
from sqlalchemy import func
from fastapi import HTTPException
from auth import *
from fuzzywuzzy import fuzz
from fuzzywuzzy import process



def salvar_pesquisa(termo: str, categoria: str, db: Session, usuario_id: int = None):
    """
    Função para salvar a pesquisa do usuário no banco de dados.
    
    Args:
        termo (str): O termo pesquisado.
        categoria (str): A categoria relacionada ao termo.
        db (Session): Sessão do banco de dados.
        usuario_id (int, opcional): O ID do usuário, se estiver logado.
    """
    pesquisa = Pesquisa(
        termo_pesquisa=termo,
        categoria_pesquisa=categoria,
        data_pesquisa=datetime.utcnow(),
        usuario_id=usuario_id  # Se o usuário não estiver logado, o ID será None
    )
    db.add(pesquisa)
    db.commit()
    db.refresh(pesquisa)


def fuzzy_search(query: str, choices: list, threshold: int = 80):
    """
    Realiza a correspondência fuzzy entre o termo de pesquisa e os dados dos produtos.
    Retorna os itens que possuem uma similaridade superior ao limiar (threshold).
    """
    results = []
    for choice in choices:
        ratio = fuzz.partial_ratio(query.lower(), choice.lower())
        if ratio >= threshold:  # Se a correspondência for maior ou igual ao limiar
            results.append((choice, ratio))
    return results

def executar_pesquisa_avancada(
    termo: str, 
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 1
):
    """
    Pesquisa avançada por produtos com palavras-chave usando fuzzy matching.
    """
    termos = termo.split()

    # Iniciar a query com produtos ativos
    query = db.query(Produto).filter(Produto.ativo == True)

    # Buscar correspondências fuzzy para cada palavra-chave
    if termos:
        conditions = []
        for palavra in termos:
            # Usar fuzzy matching nos campos do produto
            matched_nome = fuzzy_search(palavra, [p.nome for p in query.all()])
            matched_descricao = fuzzy_search(palavra, [p.descricao for p in query.all()])
            matched_categoria = fuzzy_search(palavra, [p.categoria for p in query.all()])
            
            # Adicionar filtros baseados nos matches encontrados
            conditions.append(
                or_(
                    *[Produto.nome.ilike(f"%{nome}%") for nome, _ in matched_nome],
                    *[Produto.descricao.ilike(f"%{descricao}%") for descricao, _ in matched_descricao],
                    *[Produto.categoria.ilike(f"%{categoria}%") for categoria, _ in matched_categoria]
                )
            )
        query = query.filter(or_(*conditions))

    # Garantir que o offset seja válido (não negativo)
    if offset < 1:
        offset = 1

    # Aplicar a paginação
    produtos = query.offset((offset - 1) * limit).limit(limit).all()

    # Caso não encontre produtos, salvar a pesquisa para referência futura
    if not produtos:
        salvar_pesquisa(termo=termo, categoria=None, db=db, usuario_id=user_id)
        return []

    # Processar as informações dos produtos encontrados
    return [
        {
            "id": produto.id,
            "title": produto.nome,
            "thumb": produto.capa,
            "images": produto.fotos,
            "price": float(produto.preco),
            "description": produto.descricao,
            "category": produto.categoria,
            "state": produto.estado,
            "province": produto.provincia,
            "district": produto.distrito,
            "user": {
                "id": produto.usuario.id,
                "name": produto.usuario.nome,
                "avatar": produto.usuario.foto_perfil,
                "average_stars": calcular_media_estrelas(produto.usuario.id, db),
            },
            "liked": user_id in [like.user_id for like in produto.likes] if user_id else None,
        }
        for produto in produtos
    ]


def calcular_media_estrelas(usuario_id: int, db: Session):
    """
    Calcula a média de estrelas de um usuário baseado nas avaliações.
    """
    avaliacoes = db.query(Avaliacao).filter(Avaliacao.avaliado_id == usuario_id).all()
    if not avaliacoes:
        return None  # Sem avaliações
    soma_estrelas = sum(avaliacao.estrelas for avaliacao in avaliacoes)
    return round(soma_estrelas / len(avaliacoes), 2)
def eliminar_pesquisa(db: Session, pesquisa_id: int = None, usuario_id: int = None):
    """
    Elimina uma pesquisa específica ou todas as pesquisas de um usuário.
    
    Args:
        db (Session): Sessão do banco de dados.
        pesquisa_id (int, opcional): ID da pesquisa a ser eliminada.
        usuario_id (int, opcional): ID do usuário cujas pesquisas devem ser eliminadas.
    
    Raises:
        HTTPException: Se a pesquisa ou usuário não forem encontrados.
    
    Returns:
        Mensagem de sucesso.
    """
    if pesquisa_id:
        # Deletar uma pesquisa específica
        pesquisa = db.query(Pesquisa).filter(Pesquisa.id == pesquisa_id).first()
        if not pesquisa:
            raise HTTPException(status_code=404, detail="Pesquisa não encontrada.")
        db.delete(pesquisa)
    elif usuario_id:
        # Deletar todas as pesquisas de um usuário
        pesquisas = db.query(Pesquisa).filter(Pesquisa.usuario_id == usuario_id).all()
        if not pesquisas:
            raise HTTPException(status_code=404, detail="Nenhuma pesquisa encontrada para esse usuário.")
        for pesquisa in pesquisas:
            db.delete(pesquisa)
    else:
        raise HTTPException(status_code=400, detail="ID da pesquisa ou do usuário deve ser fornecido.")
    
    db.commit()
    return {"msg": "Pesquisa(s) eliminada(s) com sucesso."}




def listar_pesquisas(db: Session, usuario_id: int = None, page: int = 1, limit: int = 10):
    """
    Lista todas as pesquisas realizadas, com a possibilidade de filtrar por usuário específico.
    
    Args:
        db (Session): Sessão do banco de dados.
        usuario_id (int, opcional): ID do usuário para filtrar as pesquisas (ou None para listar todas).
        page (int): Página de resultados (padrão: 1).
        limit (int): Limite de resultados por página (padrão: 10).
    
    Returns:
        Lista de pesquisas.
    """
    query = db.query(Pesquisa)
    
    # Se um usuário for especificado, filtra as pesquisas desse usuário
    if usuario_id:
        query = query.filter(Pesquisa.usuario_id == usuario_id)
    
    # Paginação
    pesquisas = query.offset((page - 1) * limit).limit(limit).all()
    
    return pesquisas


def calcular_peso_categorias_mais_pesquisadas(db: Session, top_n: int = 5):
    """
    Calcula o peso (frequência de pesquisa) das categorias mais pesquisadas.
    
    Args:
        db (Session): Sessão do banco de dados.
        top_n (int): Número de categorias mais pesquisadas a serem consideradas (padrão: 5).
    
    Returns:
        Lista de dicionários com categorias e seus pesos (quantidade de pesquisas).
    """
    # Seleciona as categorias mais pesquisadas e conta o número de vezes que foram pesquisadas
    categorias_mais_pesquisadas = db.query(
        Pesquisa.categoria_pesquisa,
        func.count(Pesquisa.categoria_pesquisa).label('total_pesquisas')
    ).group_by(Pesquisa.categoria_pesquisa).order_by(func.count(Pesquisa.categoria_pesquisa).desc()).limit(top_n).all()

    resultados = []
    
    # Cria a lista de resultados com categoria e peso (total de pesquisas)
    for categoria, total_pesquisas in categorias_mais_pesquisadas:
        resultados.append({
            "categoria": categoria,
            "peso": total_pesquisas  # Peso é o número de pesquisas realizadas para essa categoria
        })
    
    return resultados
