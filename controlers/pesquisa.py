from sqlalchemy.orm import Session
from controlers.produto import *
from sqlalchemy import or_
from datetime import datetime
from fastapi import APIRouter,Form,File,Query
from models import Produto,Pesquisa,Usuario,Comentario,produto_likes
from sqlalchemy import func
from fastapi import HTTPException
from auth import *



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


# Registra a ação de pesquisa
def executar_pesquisa_avancada(
    termo: str, 
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 1
):
    """
    Pesquisa avançada por produtos com paginação e filtros.
    """
    termos = termo.split()
    query = db.query(Produto).filter(Produto.ativo == True)

    # Adicionar os filtros para as colunas
    for palavra in termos:
        query = query.filter(
            or_(
                Produto.nome.ilike(f"%{palavra}%"),
                Produto.descricao.ilike(f"%{palavra}%"),
                Produto.categoria.ilike(f"%{palavra}%"),
                Produto.detalhes.ilike(f"%{palavra}%"),
                Produto.tipo.ilike(f"%{palavra}%"),
                Produto.provincia.ilike(f"%{palavra}%"),
                Produto.estado.ilike(f"%{palavra}%"),
                Produto.distrito.ilike(f"%{palavra}%")
            )
        )

    # Adicionar paginação
    produtos = query.offset(offset * limit).limit(limit).all()
    categoria = produtos[0].categoria if produtos else None

    # Salvar a pesquisa, caso nenhum produto seja encontrado
    if not produtos:
        salvar_pesquisa(termo=termo, categoria=categoria, db=db, usuario_id=user_id)
        return []

    produtos_ordenados = combinar_produtos(produtos, db)
    produtos_paginados = produtos_ordenados[offset: offset + limit]

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first() if user_id else None
    def calcular_media_estrelas(usuario_id: int):
        avaliacoes = db.query(Avaliacao).filter(Avaliacao.avaliado_id == usuario_id).all()
        if not avaliacoes:
            return None  # Sem avaliações
        soma_estrelas = sum(avaliacao.estrelas for avaliacao in avaliacoes)
        return round(soma_estrelas / len(avaliacoes), 2)

    return [
        {
            "id": produto.id,
            "title": produto.nome,
            "thumb": produto.capa,
            "images": produto.fotos,
            "price": float(produto.preco),
            "stock_quantity": produto.quantidade_estoque,
            "state": produto.estado,
            "province": produto.provincia,
            "district": produto.distrito,
            "location": produto.localizacao,
            "review": produto.revisao,
            "availability": produto.disponiblidade,
            "description": produto.descricao,
            "category": produto.categoria,
            "details": produto.detalhes,
            "type": produto.tipo,
            "views": produto.visualizacoes,
            "active": produto.ativo,
            "customer_id": produto.CustomerID,
            "likes": produto.likes,
            "slug": produto.slug,
            "time": calcular_tempo_publicacao(produto.data_publicacao),
            "user": {
                "id": produto.usuario.id,
                "name": produto.usuario.nome,
                "avatar": produto.usuario.foto_perfil,
                "average_stars": calcular_media_estrelas(produto.usuario.id),  # Média de estrelas do usuário
            },
            "liked": usuario in produto.usuarios_que_deram_like if usuario else None,
            "comments": [
                {
                    "id": comentario.id,
                    "text": comentario.comentario,
                    "date": calcular_tempo_publicacao(comentario.data_comentario),
                    "user": {
                        "id": comentador.id,
                        "name": comentador.nome,
                        "avatar": comentador.foto_perfil
                    }
                }
                for comentario, comentador in (
                    db.query(Comentario, Usuario)
                    .join(Usuario, Usuario.id == Comentario.usuarioID)
                    .filter(Comentario.produtoID == produto.id)
                    .all()
                )
            ]
        }
        for produto in produtos_paginados
    ]

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
