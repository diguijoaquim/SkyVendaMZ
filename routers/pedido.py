from controlers.pedido import *
from schemas import *
from auth import *
from fastapi import APIRouter,Form,Query

router=APIRouter(prefix="/pedidos",tags=["rotas de pedido"])


@router.get("/{user_id}/verificar_saldo/")
def verificar_saldo(user_id: int, db: Session = Depends(get_db)):
    try:
        return verificar_integridade_saldo(db, user_id)  # Ordem correta dos parâmetros
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pedido_id}/aceitar/")
def aceitar_pedido_route(pedido_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    return aceitar_pedido(db, pedido_id, current_user.id)

@router.post("/{pedido_id}/confirmar-recebimento/")
def confirmar_recebimento_route(pedido_id: int, cliente_id: int, db: Session = Depends(get_db)):
    return confirmar_recebimento_cliente(db, pedido_id, cliente_id)

@router.post("/{pedido_id}/confirmar-pagamento/")
def confirmar_pagamento_route(pedido_id: int, CustomerID: int, db: Session = Depends(get_db)):
    return confirmar_pagamento_vendedor(db, pedido_id, CustomerID)


@router.delete("/pedidos/{pedido_id}")
def delete_pedidos(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido =delete_pedido(db=db, pedido_id=pedido_id)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return db_pedido

@router.delete("/item_pedidos/{item_pedido_id}")
def delete_item_pedido(item_pedido_id: int, db: Session = Depends(get_db)):
    db_item_pedido = delete_item_pedido(db=db, item_pedido_id=item_pedido_id)
    if db_item_pedido is None:
        raise HTTPException(status_code=404, detail="ItemPedido not found")
    return db_item_pedido



# Rota para listar todos os pedidos feitos pelo usuário autenticado
@router.get("/feitos", response_model=List[dict])
def get_pedidos_feitos(
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    pedidos_feitos = db.query(Pedido).filter(Pedido.customer_id == current_user.id).all()

    if not pedidos_feitos:
        raise HTTPException(status_code=404, detail="Nenhum pedido feito encontrado.")

    return [
        {
            "id": pedido.id,
            "customer_id": pedido.customer_id,
            "produto_id": pedido.produto_id,
            "quantidade": pedido.quantidade,
            "preco_total": float(pedido.preco_total) if pedido.preco_total else None,
            "data_pedido": pedido.data_pedido.isoformat() if pedido.data_pedido else None,
            "status": pedido.status,
            "aceito_pelo_vendedor": pedido.aceito_pelo_vendedor,
            "tipo": pedido.tipo,
            "recebido_pelo_cliente": pedido.recebido_pelo_cliente,
            "data_aceite": pedido.data_aceite.isoformat() if pedido.data_aceite else None,
            "data_envio": pedido.data_envio.isoformat() if pedido.data_envio else None,
            "data_entrega": pedido.data_entrega.isoformat() if pedido.data_entrega else None,
        }
        for pedido in pedidos_feitos
    ]




# Rota para listar os pedidos recebidos pelo usuário autenticado
@router.get("/recebidos", response_model=List[dict])
def get_pedidos_recebidos(
    db: Session = Depends(get_db), 
    current_user:Usuario = Depends(get_current_user)
):
    pedidos_recebidos = (
        db.query(Pedido)
        .join(Pedido.produto)  # Relacionamento com Produto
        .filter(Pedido.produto.has(CustomerID=current_user.id))  # Verifica se o produto pertence ao vendedor atual
        .all()
    )

    if not pedidos_recebidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido recebido encontrado.")

    return [
        {
            "id": pedido.id,
            "customer_id": pedido.customer_id,
            "produto_id": pedido.produto_id,
            "quantidade": pedido.quantidade,
            "preco_total": float(pedido.preco_total) if pedido.preco_total else None,
            "data_pedido": pedido.data_pedido.isoformat() if pedido.data_pedido else None,
            "status": pedido.status,
            "aceito_pelo_vendedor": pedido.aceito_pelo_vendedor,
            "tipo": pedido.tipo,
            "recebido_pelo_cliente": pedido.recebido_pelo_cliente,
            "data_aceite": pedido.data_aceite.isoformat() if pedido.data_aceite else None,
            "data_envio": pedido.data_envio.isoformat() if pedido.data_envio else None,
            "data_entrega": pedido.data_entrega.isoformat() if pedido.data_entrega else None,
        }
        for pedido in pedidos_recebidos
    ]





@router.get("/", response_model=List[dict])
def listar_pedidos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    # Busca pedidos feitos pelo usuário
    pedidos_feitos = (
        db.query(Pedido)
        .filter(Pedido.customer_id == current_user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Busca pedidos recebidos pelo usuário (como vendedor)
    pedidos_recebidos = (
        db.query(Pedido)
        .join(Produto, Produto.id == Pedido.produto_id)
        .filter(Produto.CustomerID == current_user.id)  # Produto vinculado ao vendedor
        .offset(offset)
        .limit(limit)
        .all()
    )

    def obter_dados_produto_e_usuario(pedido):
        produto = db.query(Produto).filter(Produto.id == pedido.produto_id).first()
        vendedor = db.query(Usuario).filter(Usuario.id == produto.CustomerID).first()
        comprador = db.query(Usuario).filter(Usuario.id == pedido.customer_id).first()
        return {
            "foto_capa": produto.capa if produto else None,
            "nome_vendedor": vendedor.nome if vendedor else None,
            "nome_comprador": comprador.nome if comprador else None,
        }

    # Combina os resultados e inclui o tipo de pedido ("feito" ou "recebido")
    todos_pedidos = [
        {
            "id": pedido.id,
            "customer_id": pedido.customer_id,
            "produto_id": pedido.produto_id,
            "quantidade": pedido.quantidade,
            "preco_total": float(pedido.preco_total) if pedido.preco_total else None,
            "data_pedido": pedido.data_pedido.isoformat() if pedido.data_pedido else None,
            "status": pedido.status,
            "aceito_pelo_vendedor": pedido.aceito_pelo_vendedor,
            "compra": "compra",  # Pedido feito pelo usuário
            "recebido_pelo_cliente": pedido.recebido_pelo_cliente,
            "data_aceite": pedido.data_aceite.isoformat() if pedido.data_aceite else None,
            "data_envio": pedido.data_envio.isoformat() if pedido.data_envio else None,
            "data_entrega": pedido.data_entrega.isoformat() if pedido.data_entrega else None,
            **obter_dados_produto_e_usuario(pedido),
        }
        for pedido in pedidos_feitos
    ] + [
        {
            "id": pedido.id,
            "customer_id": pedido.customer_id,
            "produto_id": pedido.produto_id,
            "quantidade": pedido.quantidade,
            "preco_total": float(pedido.preco_total) if pedido.preco_total else None,
            "data_pedido": pedido.data_pedido.isoformat() if pedido.data_pedido else None,
            "status": pedido.status,
            "aceito_pelo_vendedor": pedido.aceito_pelo_vendedor,
            "venda": "venda",  # Pedido recebido pelo usuário
            "recebido_pelo_cliente": pedido.recebido_pelo_cliente,
            "data_aceite": pedido.data_aceite.isoformat() if pedido.data_aceite else None,
            "data_envio": pedido.data_envio.isoformat() if pedido.data_envio else None,
            "data_entrega": pedido.data_entrega.isoformat() if pedido.data_entrega else None,
            **obter_dados_produto_e_usuario(pedido),
        }
        for pedido in pedidos_recebidos
    ]

    if not todos_pedidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado.")

    return todos_pedidos


@router.put("/pedido/{pedido_id}")
def update_pedido(pedido_id: int, pedido: PedidoUpdate, db: Session = Depends(get_db)):
    db_pedido = update_pedido(db=db, pedido_id=pedido_id, pedido=pedido)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return db_pedido

# Rota para pegar os pedidos recebidos por um usuário específico
@router.get("/recebido/{user_id}")
def pedidos_recebidos(user_id: int, db: Session = Depends(get_db)):
    return get_pedidos_recebidos(db, user_id)

# Rota para pegar os pedidos feitos por um usuário específico
@router.get("/feito/{user_id}")
def pedidos_feitos(user_id: int, db: Session = Depends(get_db)):
    return get_pedidos_feitos(db, user_id)

@router.get("/{pedido_id}")
def read_pedido(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido = get_pedido(db=db, pedido_id=pedido_id)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido not found")
    return db_pedido

@router.post("/pedidos/criar/")
def criar_pedido(
    produto_id: int=Form(...),
    quantidade: int=Form(...),
    tipo: Optional[str] = Form(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Rota para criar um pedido.

    Args:
    - produto_id (int): ID do produto.
    - quantidade (int): Quantidade desejada.
    - tipo (str): Tipo do pedido ("normal" ou "fora do sistema").
    - db: Sessão do banco de dados.
    - current_user: Usuário autenticado.

    Returns:
    - Pedido criado.
    """
    # Cria o objeto PedidoCreate
    pedido_data = PedidoCreate(
        produto_id=produto_id,
        quantidade=quantidade,
        customer_id=current_user.id,
        tipo=tipo
    )

    # Chama a função de criação do pedido
    return create_pedido_db(pedido=pedido_data, db=db)

# Rota para confirmar um pedido
@router.post("/pedidos/{pedido_id}/confirmar/")
def confirmar_pedid(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return aceitar_pedido(pedido_id=pedido_id, db=db, CustomerID=current_user.id)
