from controlers.admin import *
from controlers.usuario import listar_usuarios_nao_verificados
from schemas import *
from controlers.info_usuario import *
from models import InfoUsuario,Produto,Transacao,Wallet
from auth import *
from sqlalchemy import func
from controlers.usuario import ativar_usuario,delete_usuario_db,desativar_usuario
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter,Query
from fastapi import APIRouter, Depends, HTTPException, status,Form,Body,Query

router=APIRouter(prefix="/admin", tags=["rotas de admin"] )






@router.post("/token")
def login_admin(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(admin.id)}, role="admin")  # Usando o ID do admin no token
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/usuario/{usuario_id}/revisao")
def revisar_usuario(usuario_id: int, nova_revisao: str, motivo: str = None, db: Session = Depends(get_db)):
    # Recupera o InfoUsuario baseado no ID do usuário
    db_info_usuario = db.query(InfoUsuario).filter(InfoUsuario.usuario_id == usuario_id).first()
    if not db_info_usuario:
        raise HTTPException(status_code=404, detail="InfoUsuario não encontrado.")

    # Chama a função para atualizar a revisão e enviar a notificação
    return update_revisao_info_usuario(db_info_usuario, nova_revisao, db, motivo)

# Admin routes
@router.post("/resgistro")
def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    return register_admin(db=db, admin=admin)


@router.get("/{admin_id}")
def read_admins(admin_id: int, db: Session = Depends(get_db)):
    db_admin = get_admin(db=db, admin_id=admin_id)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin


@router.delete("/delete/user/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    db_usuario = delete_usuario_db(db=db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"msg": "Usuário excluído com sucesso"}


@router.delete("/delete/{admin_id}")
def delete_admins(admin_id: int, db: Session = Depends(get_db)):
    db_admin = delete_admin(db=db, admin_id=admin_id)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin


@router.get("/usuarios/nao_verificados/")
def obter_usuarios_nao_verificados(db: Session = Depends(get_db)):
    """
    Rota para obter todos os usuários não verificados.
    
    Returns:
        List[Usuario]: Lista de usuários não verificados.
    """
    usuarios_nao_verificados = listar_usuarios_nao_verificados(db=db)
    return usuarios_nao_verificados

@router.put("/admins/{admin_id}")
def update_admins(admin_id: int, admin: AdminUpdate, db: Session = Depends(get_db)):
    db_admin = update_admin(db=db, admin_id=admin_id, admin=admin)
    if db_admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

# Rota para desativar o usuário
@router.put("/usuario/{usuario_id}/desativar")
def desativar_usuario_route(usuario_id: int, db: Session = Depends(get_db)):
    return desativar_usuario(db, usuario_id)

# Rota para ativar o usuário
@router.put("/usuario/{usuario_id}/ativar")
def ativar_usuario_route(usuario_id: int, db: Session = Depends(get_db)):
    return ativar_usuario(db, usuario_id)


@router.delete("/categorias/{categoria_id}")
def delete_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria =delete_categoria(db=db, categoria_id=categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria not found")
    return db_categoria





@router.get("/usuarios/", response_model=dict)
def listar_usuarios(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários com paginação, incluindo o total de usuários e total de produtos postados por cada um.
    """
    total_usuarios = db.query(Usuario).count()
    usuarios = (
        db.query(Usuario)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    resultado = []
    for usuario in usuarios:
        total_produtos = db.query(Produto).filter(Produto.CustomerID == usuario.id).count()
        resultado.append({
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "total_produtos": total_produtos,
            "saldo": usuario.wallet.saldo_principal if usuario.wallet else 0.0,
        })

    return {
        "total_usuarios": total_usuarios,
        "usuarios": resultado,
        "page": page,
        "per_page": per_page,
    }


@router.get("/usuarios/pendentes/", response_model=dict)
def listar_usuarios_pendentes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários com estado pendente, com paginação.
    """
    total_pendentes = db.query(Usuario).filter(Usuario.revisao == "pendente").count()
    usuarios = (
        db.query(Usuario)
        .filter(Usuario.revisao == "pendente")
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total_pendentes": total_pendentes,
        "usuarios": usuarios,
        "page": page,
        "per_page": per_page,
    }


@router.get("/usuarios/verificados/")
def listar_usuarios_verificados(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários verificados, com paginação.
    """
    total_verificados = db.query(Usuario).filter(Usuario.revisao == "sim").count()
    usuarios = (
        db.query(Usuario)
        .filter(Usuario.revisao == "sim")
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total_verificados": total_verificados,
        "usuarios": usuarios,
        "page": page,
        "per_page": per_page,
    }

@router.get("/sistema/resumo/", response_model=dict)
def resumo_sistema(db: Session = Depends(get_db)):
    """
    Retorna um resumo do sistema, incluindo o saldo total, total de produtos ativos e total de usuários.
    """
    # Calcular o saldo total
    saldo_total = db.query(func.sum(Wallet.saldo_principal)).scalar() or 0.0

    # Contar os produtos ativos
    total_produtos_ativos = db.query(Produto).filter(Produto.ativo == True).count()

    # Contar o total de produtos
    total_produtos = db.query(Produto).count()

    # Contar o total de usuários
    total_usuarios = db.query(Usuario).count()

    return {
        "saldo_total": saldo_total,
        "total_produtos_ativos": total_produtos_ativos,
        "total_produtos": total_produtos,
        "total_usuarios": total_usuarios,
    }


@router.get("/{usuario_id}/transacoes")
def listar_transacoes_usuario(
    usuario_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
   
):
    """
    Lista as transações de um usuário específico com paginação.
    """

    # Verificar se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


    # Paginação
    offset = (page - 1) * page_size
    transacoes = (
        db.query(Transacao)
        .filter(Transacao.usuario_id == usuario_id)
        .order_by(Transacao.data_hora.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    if not transacoes:
        return []

    return [
        {
            "id": transacao.id,
            "msisdn": transacao.msisdn,
            "valor": float(transacao.valor),
            "referencia": transacao.referencia,
            "status": transacao.status,
            "data_hora": transacao.data_hora,
            "tipo": transacao.tipo,
        }
        for transacao in transacoes
    ]
