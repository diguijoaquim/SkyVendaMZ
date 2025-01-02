import os
import uuid
import shutil
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import List, Optional
from models import *
from schemas import ProdutoCreate, ProdutoUpdate
from datetime import datetime, timedelta
from sqlalchemy import func
from PIL import Image
from controlers.pedido import enviar_notificacao
from sqlalchemy.future import select
import random
from decimal import Decimal
from unidecode import unidecode
from slugify import slugify
from PIL import Image
from controlers.utils import *
import shutil
from controlers.taxas import calcular_taxa_publicacao,calcular_custo_anuncio


PRODUCT_UPLOAD_DIR = "uploads/produto"
STATUS_UPLOAD_DIR= "uploads/status"
os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)
os.makedirs(STATUS_UPLOAD_DIR, exist_ok=True)


def save_image(file: UploadFile, upload_dir: str, max_size=(300, 300)) -> str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")
    
    file_extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Abrir a imagem para redimensionamento
    try:
        with Image.open(file.file) as img:
            img = img.convert("RGB")  # Converte para RGB se necessário
            img.thumbnail(max_size)  # Redimensiona mantendo a proporção
            img.save(file_path, format=file_extension.upper() if file_extension != "jpg" else "JPEG", quality=85)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a imagem: {str(e)}")
    
    return unique_filename

# Função para salvar imagens adicionais sem redimensionar
def save_image_original(file: UploadFile, upload_dir: str) -> str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")
    
    file_extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar a imagem: {str(e)}")
    
    return unique_filename

# Função para salvar múltiplas imagens adicionais
def save_images(files: List[UploadFile], upload_dir: str) -> List[str]:
    return [save_image_original(file, upload_dir) for file in files]

# Função para criar um produto no banco de dados
def create_produto_db_with_image(
    db: Session,
    produto: ProdutoCreate,
    files: List[UploadFile],
    user_id: int,
    extra_files: List[UploadFile],
):
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Você está desativado.")

    # Verifica se o usuário passou pela revisão
    info_usuario = db.query(InfoUsuario).filter(InfoUsuario.usuario_id == user_id).first()
    if not info_usuario or info_usuario.revisao != "sim":
        raise HTTPException(status_code=403, detail="Usuário não passou pela revisão e não pode publicar produtos.")

    # Verifica se imagens foram enviadas
    if not files:
        raise HTTPException(status_code=400, detail="Nenhuma imagem foi enviada.")
    
    # Verifica se a conta PRO expirou
    usuario.verificar_expiracao_pro()

    # Verifica limite de publicações diárias
    hoje = datetime.utcnow().date()
    produtos_hoje = db.query(Produto).filter(
        Produto.CustomerID == user_id,
        Produto.data_publicacao >= hoje
    ).count()

    LIMITE_DIARIO_NORMAL = 2  # Limite diário para contas normais

    # Obter a carteira do usuário
    wallet = db.query(Wallet).filter(Wallet.usuario_id == user_id).first()
    if not wallet:
        wallet = Wallet(usuario_id=usuario.id, saldo_principal=Decimal("0.0"))
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    # Calcula a taxa de publicação
    taxa_publicacao = calcular_taxa_publicacao(Decimal(produto.preco))

    # Verifica limites e custos de publicação
    if not usuario.conta_pro:
        if produtos_hoje >= LIMITE_DIARIO_NORMAL:
            if wallet.saldo_principal >= taxa_publicacao:
                wallet.saldo_principal -= taxa_publicacao

                # Registra a transação
                transacao = Transacao(
                    usuario_id=usuario.id,
                    msisdn=usuario.username,
                    tipo="saida",
                    valor=taxa_publicacao,
                    referencia="Publicação de produto adicional",
                    status="sucesso"
                )
                db.add(transacao)
                db.commit()
            elif wallet.saldo_principal + wallet.bonus >= taxa_publicacao:
                wallet.bonus -= taxa_publicacao - wallet.saldo_principal
                wallet.saldo_principal = Decimal("0.0")
            else:
                raise HTTPException(status_code=403, detail="Saldo insuficiente para publicar o produto.")
    
    # Salva a imagem de capa redimensionada
    #capa_filename = save_image(files[0], PRODUCT_UPLOAD_DIR, max_size=(300, 300))
    capa_filename = save_image(files[0], PRODUCT_UPLOAD_DIR)

    # Salva as imagens adicionais sem redimensionamento
    image_filenames = save_images(extra_files, PRODUCT_UPLOAD_DIR)
    
    # Cria o produto no banco de dados
    db_produto = Produto(
        **produto.dict(),
        capa=capa_filename,
        fotos=",".join(image_filenames),
        data_publicacao=datetime.utcnow()
    )
    
    db.add(db_produto)
    db.commit()
    
    # Envia notificação de publicação
    mensagem_notificacao = f"{usuario.nome} publicou um novo produto!"
    enviar_notificacoes_para_seguidores(db, usuario.id, mensagem_notificacao)
    
    return db_produto

def get_produtos_promovidos(db: Session):
    """
    Retorna todos os produtos que estão atualmente promovidos (anunciados).
    """
    # Busca os produtos que possuem anúncios válidos (não expirados)
    produtos_promovidos = db.query(Produto).join(Anuncio).filter(
        Anuncio.data_expiracao > datetime.utcnow()
    ).all()

    if not produtos_promovidos:
        raise HTTPException(status_code=404, detail="Nenhum produto promovido encontrado.")

    return produtos_promovidos


def seguir_usuario(db: Session, usuario_id: int, seguidor_id: int) -> bool:
    # Verificar se o seguidor e o usuário existem
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    seguidor = db.query(Usuario).filter(Usuario.id == seguidor_id).first()

    if usuario.ativo==False:
        raise HTTPException(status_code=404, detail="o usuario esta desactivado")
    if seguidor.ativo==False:
        raise HTTPException(status_code=404, detail="voce esta desactivado")
    
    if not usuario or not seguidor:
        raise HTTPException(status_code=404, detail="Usuário ou seguidor não encontrado.")
    
    if usuario_id == seguidor_id:
        raise HTTPException(status_code=400, detail="Você não pode seguir a si mesmo.")

    # Verificar se já está seguindo
    seguimento_existente = db.query(Seguidor).filter(
        Seguidor.usuario_id == usuario_id,
        Seguidor.seguidor_id == seguidor_id
    ).first()

    if seguimento_existente:
        # Deixar de seguir
        db.delete(seguimento_existente)
        db.commit()
        return False  # Deixou de seguir
    else:
        # Seguir
        novo_seguidor = Seguidor(usuario_id=usuario_id, seguidor_id=seguidor_id)
        db.add(novo_seguidor)
        db.commit()

        # Enviar notificação para o usuário que está sendo seguido
        mensagem = f"{seguidor.nome} começou a seguir você!"
        enviar_notificacao(db, usuario_id, mensagem)

        return True  # Começou a seguir

  
def calcular_tempo_publicacao(data_publicacao):
    """
    Calcula o tempo decorrido desde a data de publicação e retorna uma string legível.
    """
    agora = datetime.utcnow()
    delta = agora - data_publicacao

    # Definindo intervalos de tempo em segundos
    segundos = delta.total_seconds()
    if segundos < 60:
        return f"há {int(segundos)} segundo{'s' if segundos > 1 else ''}"
    minutos = segundos / 60
    if minutos < 60:
        return f"há {int(minutos)} minuto{'s' if minutos > 1 else ''}"
    horas = minutos / 60
    if horas < 24:
        return f"há {int(horas)} hora{'s' if horas > 1 else ''}"
    dias = horas / 24
    if dias < 30:
        return f"há {int(dias)} dia{'s' if dias > 1 else ''}"
    semanas = dias / 7
    if semanas < 4:
        return f"há {int(semanas)} semana{'s' if semanas > 1 else ''}"
    
    # Se passou mais de um mês, retorna a data de publicação no formato "dd/mm/aaaa"
    return data_publicacao.strftime('%d/%m/%Y')


# Função para obter seguidores de um usuário
def get_seguidores(usuario_id: int, db: Session):
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Obter a lista de pessoas que o usuário segue
    seguindo = db.query(Seguidor).filter(Seguidor.usuario_id == usuario_id).all()

    # Obter o total de pessoas que ele segue
    total_seguindo = db.query(func.count(Seguidor.id)).filter(Seguidor.usuario_id == usuario_id).scalar()

    # Formatar a lista de seguidores com detalhes dos usuários
    seguindo_list = [
        {
            "id": seguidor.seguidor.id,
            "nome": seguidor.seguidor.nome,
            "username": seguidor.seguidor.username,
            "email": seguidor.seguidor.email
        } 
        for seguidor in seguindo
    ]

    return {
        "total_seguindo": total_seguindo,
        "seguindo": seguindo_list
    }
def toggle_like_produto(db: Session, produto_slug: str, user_id: int):
    produto = db.query(Produto).filter(Produto.slug == produto_slug).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    like_existente = db.query(produto_likes).filter_by(produto_id=produto.id, usuario_id=user_id).first()

    if like_existente:
        produto.likes -= 1
        db.execute(
            produto_likes.delete()
            .where(produto_likes.c.produto_id == produto.id)
            .where(produto_likes.c.usuario_id == user_id)
        )
        message = "Like removido com sucesso!"
        acao = "remover_like"
    else:
        produto.likes += 1
        db.execute(
            produto_likes.insert().values(produto_id=produto.id, usuario_id=user_id)
        )
        message = "Like adicionado com sucesso!"
        acao = "adicionar_like"

    db.commit()

    # Registra a ação de like
    # Registra a ação com a categoria
    registrar_acao_com_categoria(
        db=db,
        usuario_id=user_id,
        tipo_acao="like",
        produto_id=produto.id,
        entidade="Produto",
        detalhes={"produto_id": produto.id}
    )

    return {"message": message, "total_likes": produto.likes}






def reativar_produto(produto_id: int, current_user: Usuario, db: Session):
    # Buscar o produto no banco de dados
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    if produto.ativo:
        raise HTTPException(status_code=400, detail="Produto já está ativo.")

    # Verificar saldo do usuário
    if current_user.saldo < 25:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para reativar o produto.")
    
    # Descontar saldo e reativar o produto
    current_user.saldo -= 25
    produto.ativo = True
    produto.data_publicacao = datetime.utcnow()  # Atualizar a data de publicação para reiniciar o ciclo de 30 dias
    db.commit()

    return {"msg": "Produto reativado com sucesso!"}


def atualizar_status_produtos(db: Session):
    produtos = db.query(Produto).all()
    for produto in produtos:
        if produto.ativo and datetime.utcnow() > produto.data_publicacao + timedelta(days=30):
            produto.ativo = False
            db.commit()

#Seb@$t!@oP@ULO//

def gerar_slug(nome_produto: str) -> str:
    nome_sem_acento = unidecode(nome_produto)  # Remove acentos e caracteres especiais
    return slugify(nome_sem_acento)  # Gera o slug amigável

def gerar_slug_unico(nome_produto: str, db: Session) -> str:
    slug_base = gerar_slug(nome_produto)
    slug = slug_base
    contador = 1

    # Verifica se já existe um produto com o mesmo slug
    while db.query(Produto).filter(Produto.slug == slug).first() is not None:
        slug = f"{slug_base}-{contador}"
        contador += 1

    return slug
def get_produto_likes(db: Session, produto_id: int):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    # Conta o número de likes do produto
    likes_count = db.query(produto_likes).filter_by(produto_id=produto_id).count()
    
    return {"produto_id": produto_id, "likes": likes_count}




def listar_anuncios_com_produtos(db: Session):
    stmt = (
        select(Anuncio, Produto)
        .join(Produto, Anuncio.produto_id == Produto.id)
    )
    result = db.execute(stmt)
    anuncios = [
        {
            "anuncio": {
                "id": anuncio.id,
                "titulo": anuncio.titulo,
                "descricao": anuncio.descricao,
                "tipo_anuncio": anuncio.tipo_anuncio,
                "produto_id": anuncio.produto_id,
                "expira_em": anuncio.expira_em.isoformat() if anuncio.expira_em else None,
                "promovido_em": anuncio.promovido_em.isoformat() if anuncio.promovido_em else None
            },
            "produto": {
                "id": produto.id,
                "nome": produto.nome,
                "descricao": produto.descricao,
                "preco": produto.preco,
                "capa":produto.capa,
                "likes":produto.likes,
                "views":produto.visualizacoes
            }
        }
        for anuncio, produto in result
    ]
    return anuncios



def get_produto_detalhado(db: Session, slug: str,usuario_id: Optional[int] = None):
    """
    Retorna os detalhes do produto, incluindo foto, nome, comentários, categoria, preço,
    nome do usuário que publicou, data, disponibilidade, total de likes e usuários que deram like,
    e incrementa o número de visualizações do produto.
    
    Args:
        db (Session): Sessão do banco de dados.
        slug (str): Slug do produto.
    
    Returns:
        dict: Detalhes do produto.
    """
    # Busca o produto pelo slug
    produto = db.query(Produto).filter(Produto.slug == slug).first()
    
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    # Incrementa o número de visualizações
    produto.visualizacoes += 1
    db.add(produto)
    db.commit()
    db.refresh(produto)
    

    # Registra a ação com a categoria
    registrar_acao_com_categoria(
        db=db,
        usuario_id=usuario_id,
        tipo_acao="visualizacao",
        produto_id=produto.id,
        entidade="Produto",
        detalhes={"produto_id": produto.id}
    )
    # Busca o usuário que publicou o produto
    usuario = db.query(Usuario).filter(Usuario.id == produto.CustomerID).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário que publicou o produto não encontrado.")
    
    # Busca os comentários do produto
    comentarios = db.query(Comentario).filter(Comentario.produtoID == produto.id).all()
    
    # Busca os likes (usuários que curtiram o produto)
    usuarios_que_deram_like = db.query(Usuario).join(produto_likes).filter(produto_likes.c.produto_id == produto.id).all()
    total_likes = len(usuarios_que_deram_like)  # Total de likes
    tempo_publicacao = calcular_tempo_publicacao(produto.data_publicacao)
    # Retorna os detalhes em um dicionário
    return {
        "nome": produto.nome,
        "detalhe": produto.detalhes,
        "tipo": produto.tipo,
        "foto_capa": produto.capa,
        "preco": produto.preco,
        "slug": produto.slug,
        "estado":produto.estado,
        "fotos": produto.fotos,
        "distrito":produto.distrito,
        "provincia":produto.provincia,
        "localizacao":produto.localizacao,
        "categoria": produto.categoria,
        "disponibilidade": produto.disponiblidade,
        "data_publicacao": tempo_publicacao,  # Supondo que exista esse campo
        "visualizacoes": produto.visualizacoes,  # Inclui o campo de visualizações
        "usuario": {
            "nome": usuario.nome,
            "email": usuario.email
        },
        "categoria": produto.categoria,
        "comentarios": [
            {
                "comentario": comentario.comentario,
                "avaliacao": comentario.avaliacao,
                "data_comentario": comentario.data_comentario
            } for comentario in comentarios
        ],
        "likes": {
            "total": total_likes,
            "usuarios": [
                {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email
                }
                for usuario in usuarios_que_deram_like
            ]
        }
    }




def enviar_notificacoes_para_seguidores(db: Session, usuario_id: int, mensagem: str):
    # Buscar seguidores
    seguidores = db.query(Seguidor).filter(Seguidor.usuario_id == usuario_id).all()

    # Enviar notificação para cada seguidor
    for seguidor in seguidores:
        nova_notificacao = Notificacao(
            usuario_id=seguidor.seguidor_id,
            mensagem=mensagem
        )
        db.add(nova_notificacao)
    db.commit()





def update_produto_db_with_images(db: Session, produto_id: str, produto: ProdutoUpdate):
    db_produto = db.query(Produto).filter(Produto.slug == produto_id).first()
    
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    # Atualiza os dados do produto
    for key, value in produto.dict().items():
        setattr(db_produto, key, value)
    
    # Se houver novas imagens, salva e atualiza
  
    db.commit()
    db.refresh(db_produto)
    
    return db_produto


def selecionar_produtos_por_peso(produtos: List[Produto], db: Session):
    """
    Ordena produtos não recentes ponderados por promoção, likes e visualizações.

    Args:
        produtos (List[Produto]): Lista de produtos não recentes.
        db (Session): Sessão do banco de dados para consultar anúncios.

    Returns:
        List[Produto]: Lista de produtos não recentes ordenados pelo peso, sem repetições.
    """
    produtos_com_peso = []

    for produto in produtos:
        # Calcular o peso baseado em visualizações e likes
        score = produto.visualizacoes + (2 * produto.likes)
        
        # Aumentar o peso se o produto estiver promovido
        anuncio = db.query(Anuncio).filter(Anuncio.produto_id == produto.id).first()
        if anuncio:
            score *= 1.5  # Ajusta o peso para produtos promovidos
        
        produtos_com_peso.append((produto, score))

    # Ordenar produtos não recentes pelo peso (pontuação), do maior para o menor
    produtos_com_peso.sort(key=lambda x: x[1], reverse=True)

    # Retornar apenas a lista de produtos, mantendo a ordem ponderada
    return [produto for produto, _ in produtos_com_peso]



def filtrar_produtos_recentes(produtos: List[Produto]):
    """
    Filtra produtos publicados nos últimos 30 minutos.

    Args:
        produtos (List[Produto]): Lista de produtos.
    
    Returns:
        List[Produto]: Lista de produtos recentes.
    """
    trinta_minutos_atras = datetime.utcnow() - timedelta(minutes=30)
    
    # Filtrando produtos onde a data_publicacao não é None e o produto foi publicado nos últimos 30 minutos
    produtos_recentes = [
        produto for produto in produtos 
        if produto.data_publicacao is not None and produto.data_publicacao > trinta_minutos_atras
    ]
    
    return produtos_recentes



def combinar_produtos(produtos: List[Produto], db: Session):
    """
    Combina produtos recentes (aleatórios) e ponderados para produtos não recentes.
    
    Args:
        produtos (List[Produto]): Lista completa de produtos.
        db (Session): Sessão do banco de dados para consultar anúncios.

    Returns:
        List[Produto]: Lista de produtos ordenados.
    """
    # Filtrar produtos recentes (últimos 30 minutos)
    produtos_recentes = filtrar_produtos_recentes(produtos)
    
    # Filtrar produtos não recentes
    produtos_nao_recentes = [produto for produto in produtos if produto not in produtos_recentes]
    
    # Embaralhar produtos recentes
    random.shuffle(produtos_recentes)
    
    # Ordenar produtos não recentes por peso
    produtos_ponderados = selecionar_produtos_por_peso(produtos_nao_recentes, db)
    
    # Combinar os resultados: Recentes primeiro, seguidos pelos ponderados
    return produtos_recentes + produtos_ponderados


def get_all_produtos(db: Session):
    """
    Função para buscar todos os produtos ativos e com revisão marcada como 'sim'.
    
    Args:
        db (Session): Sessão do banco de dados.
    
    Returns:
        List[Produto]: Lista de produtos ativos e com revisão 'sim'.
    """
    produtos = db.query(Produto).filter(Produto.ativo == True, Produto.revisao == "sim").all()

    if not produtos:
        raise HTTPException(status_code=404, detail="Nenhum produto ativo encontrado com revisão 'sim'.")
    
    return produtos


def get_produtos_by_user(db: Session, user_id: int):
    """
    Função para buscar todos os produtos de um usuário específico.
    
    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário para o qual queremos buscar os produtos.
    
    Returns:
        List[Produto]: Lista de produtos encontrados para o usuário.
    """
    produtos = db.query(Produto).filter(Produto.CustomerID == user_id).all()
    if not produtos:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado para este usuário.")
    return produtos






def promover_produto(
    produto_id: int, dias: int, db: Session, usuario_id: int, titulo: str, descricao: str, tipo: str
):
    # Busca o produto
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Busca a wallet do usuário
    wallet = db.query(Wallet).filter(Wallet.usuario_id == usuario_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira do usuário não encontrada")

    # Calcula o custo da promoção
    custo_promocao =calcular_custo_anuncio(tipo=tipo, dias=dias)  # Custo fixo de 10 MT por dia

    # Verifica se o saldo principal é suficiente
    if wallet.saldo_principal < custo_promocao:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para promover o produto")

    # Desconta o saldo principal
    wallet.saldo_principal -= custo_promocao
    db.commit()

    # Criar o anúncio vinculado ao produto
    anuncio = Anuncio(
        produto_id=produto.id,
        titulo=titulo,
        descricao=descricao,
        tipo_anuncio=tipo,
        promovido_em=datetime.utcnow(),
        expira_em=datetime.utcnow() + timedelta(days=dias),
    )
    db.add(anuncio)
    db.commit()

    return {
        "message": f"Produto promovido por {dias} dias e colocado em anúncio",
        "produto": {
            "id": produto.id,
            "nome": produto.nome,
            "preco": float(produto.preco),
        },
        "anuncio": {
            "id": anuncio.id,
            "titulo": anuncio.titulo,
            "descricao": anuncio.descricao,
            "promovido_em": anuncio.promovido_em.isoformat(),
            "expira_em": anuncio.expira_em.isoformat(),
        },
        "custo_promocao": float(custo_promocao),
        "saldo_atual": float(wallet.saldo_principal),
    }
def get_produto(db: Session, slug: str):
    """
    Recupera um produto pelo slug e incrementa o número de visualizações.

    Args:
        db (Session): Sessão do banco de dados.
        slug (str): Slug do produto.

    Returns:
        Produto: Instância do produto se encontrado, caso contrário None.
    """
    # Buscar o produto no banco de dados pelo slug
    produto = db.query(Produto).filter(Produto.slug == slug).first()

    if not produto:
        return None  # Retorna None se o produto não for encontrado

    # Incrementar o número de visualizações
    produto.visualizacoes += 1

    # Salvar as alterações no banco de dados
    db.add(produto)
    db.commit()
    db.refresh(produto)

    return produto


    return produto  # Retorna o produto atualizado


# Função para salvar imagem
def save_image(file: UploadFile, upload_dir: str) -> str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")
    
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return unique_filename

# Criar status
def criar_status_controller(usuario_id: int, conteudo: str, imagem: UploadFile, duracao_dias: int, db: Session):
    # Buscar o usuário pelo ID
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se o usuário é verificado
    info_usuario = db.query(InfoUsuario).filter(InfoUsuario.usuario_id == usuario_id).first()
    if not info_usuario or info_usuario.revisao != "sim":
        raise HTTPException(status_code=403, detail="Usuário não é verificado")

    # Verificar se o usuário tem uma carteira
    if not usuario.wallet:
        wallet = Wallet(usuario_id=usuario.id, saldo_principal=Decimal("0.0"))  # Inicializa com saldo 0
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    # Calcular o custo total do status
    custo_total = Decimal(duracao_dias) * Decimal("9.0")

    # Verificar se o saldo principal é suficiente
    if usuario.wallet.saldo_principal < custo_total:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para postar o status")

    # Deduzir o saldo principal
    usuario.wallet.saldo_principal -= custo_total

    # Processar a imagem (se houver)
    imagem_url = None
    if imagem:
        imagem_url = save_image(imagem, STATUS_UPLOAD_DIR)

    # Criar o novo status
    novo_status = Status(
        usuario_id=usuario.id,
        conteudo=conteudo,
        imagem_url=imagem_url,
        expira_em=datetime.utcnow() + timedelta(days=duracao_dias),
        custo_total=custo_total
    )

    db.add(novo_status)
    db.commit()
    db.refresh(novo_status)

    return {"message": "Status criado com sucesso", "status_id": novo_status.id}

# Visualizar status
def visualizar_status(status_id: int, db: Session):
    # Buscar o status pelo ID
    status = db.query(Status).filter(Status.id == status_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status não encontrado")

    # Incrementar contagem de visualizações
    status.visualizacoes += 1
    db.commit()

    return {"message": "Status visualizado", "visualizacoes": status.visualizacoes}

# Função para eliminar status expirados
def verificar_e_eliminar_status_expirados(db: Session):
    status_expirados = db.query(Status).filter(Status.expira_em < datetime.utcnow()).all()
    
    for status in status_expirados:
        # Se o status tiver uma imagem associada, remover o arquivo do sistema de arquivos
        if status.imagem_url:
            image_path = os.path.join(STATUS_UPLOAD_DIR, status.imagem_url)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Remover o status do banco de dados
        db.delete(status)
    
    db.commit()


# Função para enviar notificação se faltar 1 hora para expirar
def notificar_expiracao_em_uma_hora(db: Session):
    uma_hora_depois = datetime.utcnow() + timedelta(hours=1)
    status_para_notificar = db.query(Status).filter(Status.expira_em <= uma_hora_depois, Status.expira_em > datetime.utcnow()).all()
    
    for status in status_para_notificar:
        nova_notificacao = Notificacao(
            usuario_id=status.usuario_id,
            mensagem=f"Seu status expira em 1 hora. Renove se necessário.",
            data=datetime.utcnow()
        )
        db.add(nova_notificacao)
    
    db.commit()
def atualizar_status_controller(db: Session, usuario_id: int, status_id: int, dias_adicionais: int, conteudo: str = None, imagem: UploadFile = None):
    # Buscar o status pelo ID
    status = db.query(Status).filter(Status.id == status_id, Status.usuario_id == usuario_id).first()
    if not status:
        raise HTTPException(status_code=404, detail="Status não encontrado")

    # Calcular o custo adicional
    custo_adicional = Decimal(dias_adicionais) * Decimal("9.0")

    # Verificar se o usuário tem saldo suficiente
    if status.usuario.wallet.saldo_principal < custo_adicional:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para renovar o status")

    # Deduzir o saldo principal
    status.usuario.wallet.saldo_principal -= custo_adicional

    # Atualizar a data de expiração
    status.expira_em += timedelta(days=dias_adicionais)

    # Atualizar conteúdo e imagem se fornecidos
    if conteudo:
        status.conteudo = conteudo
    if imagem:
        # Chame sua função para salvar a imagem, se necessário
        imagem_url = save_image(imagem, STATUS_UPLOAD_DIR)  # Verifique se o diretório está correto
        status.imagem_url = imagem_url

    db.commit()
    db.refresh(status)

    return {"message": "Status atualizado com sucesso", "status_id": status.id}



def categorias_mais_populares(db: Session):
    """
    Retorna as categorias mais interagidas no geral.
    """
    categorias = (
        db.query(
            Log.detalhes["categoria"].cast(String).label("categoria"),  # Corrigido aqui
            func.count(Log.id).label("total_interacoes"),
        )
        .group_by(Log.detalhes["categoria"].cast(String))  # Corrigido aqui
        .order_by(func.count(Log.id).desc())
        .all()
    )

    return [{"categoria": c[0], "total_interacoes": c[1]} for c in categorias]