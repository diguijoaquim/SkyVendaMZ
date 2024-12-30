from sqlalchemy.orm import Session
from models import Pedido, Produto, Notificacao, Usuario, Wallet
from schemas import PedidoCreate, PedidoUpdate
from fastapi import HTTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models import Transacao
import smtplib
from decimal import Decimal
from datetime import datetime

def send_email(recipient: str, subject: str, body: str):
    sender_email = "jorgepaulomepia@gmail.com"  # Seu e-mail
    sender_password = "ryyuofxscbisgrre"  # Sua senha de app (senha específica do Gmail)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Servidor SMTP do Gmail
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def enviar_notificacao(db: Session, usuario_id: int, mensagem: str):
    notificacao = Notificacao(
        usuario_id=usuario_id,
        mensagem=mensagem,
        data=datetime.utcnow()
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    return notificacao


def create_pedido_db(db: Session, pedido: PedidoCreate):
    # Verifica se o produto existe
    produto = db.query(Produto).filter(Produto.id == pedido.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    # Verifica se a quantidade solicitada está disponível no estoque
    if produto.quantidade_estoque < pedido.quantidade:
        raise HTTPException(status_code=400, detail="Estoque insuficiente para o pedido.")

    if produto.CustomerID == pedido.customer_id:
        raise HTTPException(status_code=400, detail="Você não pode comprar o seu próprio produto.")

    # **Verifica se há um pedido pendente para o mesmo produto**
    pedido_pendente = (
        db.query(Pedido)
        .filter(
            Pedido.produto_id == pedido.produto_id,
            Pedido.customer_id == pedido.customer_id,
            Pedido.aceito_pelo_vendedor == False  # Pedido ainda não foi aceito
        )
        .first()
    )
    if pedido_pendente:
        raise HTTPException(
            status_code=400,
            detail="Você já tem um pedido pendente para este produto. Aguarde o vendedor aceitar antes de fazer outro."
        )

    # Calcula o preço total do pedido
    preco_total = pedido.quantidade * produto.preco

    # Se o tipo do pedido for "SkyWallet", toca o saldo do comprador e vendedor
    if pedido.tipo == "SkyWallet":
        # Verifica e congela o saldo do comprador
        wallet_comprador = db.query(Wallet).filter(Wallet.usuario_id == pedido.customer_id).first()
        if not wallet_comprador or wallet_comprador.saldo_principal < preco_total:
            raise HTTPException(status_code=400, detail="Saldo insuficiente.")

        wallet_comprador.saldo_congelado += preco_total
        wallet_comprador.saldo_principal -= preco_total

        # Atualiza o saldo congelado do vendedor
        wallet_vendedor = db.query(Wallet).filter(Wallet.usuario_id == produto.CustomerID).first()
        if not wallet_vendedor:
            raise HTTPException(status_code=404, detail="Carteira do vendedor não encontrada.")

        wallet_vendedor.saldo_congelado += preco_total

    # Cria o pedido
    db_pedido = Pedido(
        customer_id=pedido.customer_id,
        produto_id=pedido.produto_id,
        quantidade=pedido.quantidade,
        preco_total=preco_total,
        tipo=pedido.tipo,  # Define o tipo do pedido
        status="Pendente"
    )

    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)

    # Busca o e-mail do vendedor e envia notificação
    vendedor = db.query(Usuario).filter(Usuario.id == produto.CustomerID).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado.")

    vendedor_email = vendedor.email
    produto_nome = produto.nome

    email_enviado = send_email(
        recipient=vendedor_email,
        subject="Novo Pedido Recebido",
        body=f"Você recebeu um novo pedido para o produto: {produto_nome}"
    )

    if not email_enviado:
        raise HTTPException(status_code=500, detail="Falha ao enviar o e-mail de notificação.")

    try:
        mensagem = f"Você recebeu um novo pedido para o produto {produto_nome}"
        enviar_notificacao(db, vendedor.id, mensagem)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar notificação: {str(e)}")

    return db_pedido



def listar_notificacoes(db: Session, usuario_id: int):
    notificacoes = db.query(Notificacao).filter(Notificacao.usuario_id == usuario_id).all()
    return notificacoes

def get_pedidos(db: Session):
    return db.query(Pedido).all()

def get_pedido(db: Session, pedido_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return pedido

def get_pedidos_recebidos(db: Session, user_id: int):
    pedidos_recebidos = db.query(Pedido).join(Produto).filter(Produto.CustomerID == user_id).all()
    if not pedidos_recebidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido recebido encontrado para este usuário.")
    return pedidos_recebidos

def get_pedidos_feitos(db: Session, user_id: int):
    pedidos_feitos = db.query(Pedido).filter(Pedido.customer_id == user_id).all()
    
    if not pedidos_feitos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado para este usuário.")
    
    # Convertendo os pedidos para uma lista de dicionários
    pedidos_detalhados = [
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
            "produto": {
                "id": pedido.produto.id,
                "nome": pedido.produto.nome,
                "descricao": pedido.produto.descricao,
                "preco": float(pedido.produto.preco)
            } if pedido.produto else None
        }
        for pedido in pedidos_feitos
    ]
    
    return pedidos_detalhados


def update_pedido_db(db: Session, pedido_id: int, pedido: PedidoUpdate):
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    for key, value in pedido.dict().items():
        setattr(db_pedido, key, value)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def delete_pedido(db: Session, pedido_id: int):
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if db_pedido.aceito_pelo_vendedor ==1:
        raise HTTPException(status_code=403,detail="nao pode cancelar o pedido, o seu produto esta a caminho")
    # Liberar saldo congelado do comprador
    wallet_comprador = db.query(Wallet).filter(Wallet.usuario_id == db_pedido.customer_id).first()
    if wallet_comprador:
        wallet_comprador.saldo_principal += db_pedido.preco_total
        wallet_comprador.saldo_congelado -= db_pedido.preco_total

    db.delete(db_pedido)
    db.commit()
    return db_pedido

def aceitar_pedido(db: Session, pedido_id: int, vendedor_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    produto = db.query(Produto).filter(Produto.id == pedido.produto_id, Produto.CustomerID == vendedor_id).first()
    if not produto:
        raise HTTPException(status_code=403, detail="Você não tem permissão para aceitar este pedido.")

    # Verifica o tipo do pedido
    if pedido.tipo == "normal":
        # Se for um pedido normal, marca como "Concluído" diretamente
        pedido.status = "Concluido"
        pedido.data_aceite = datetime.utcnow()
    else:
        # Se não for "normal", atualiza o estado para "Aceito pelo Vendedor"
        pedido.aceito_pelo_vendedor = True
        pedido.status = "Aceito pelo Vendedor"
        pedido.data_aceite = datetime.utcnow()

    db.commit()
    db.refresh(pedido)

    return {"mensagem": "Pedido processado com sucesso.", "status": pedido.status}


def confirmar_recebimento_cliente(db: Session, pedido_id: int, cliente_id: int):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id, Pedido.customer_id == cliente_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    # Atualiza o estado para "Recebido pelo Cliente"
    pedido.recebido_pelo_cliente = True
    pedido.status = "Recebido pelo Cliente"
    db.commit()

    return {"mensagem": "Recebimento confirmado pelo cliente."}

def liberar_saldo_vendedor(db: Session, pedido: Pedido):
    # Fazer join entre Pedido e Produto
    produto = db.query(Produto).filter(Produto.id == pedido.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    # Carregar a carteira do vendedor
    wallet_vendedor = db.query(Wallet).filter(Wallet.usuario_id == produto.CustomerID).first()
    if not wallet_vendedor:
        raise HTTPException(status_code=404, detail="Carteira do vendedor não encontrada.")

    # Carregar a carteira do cliente (comprador)
    wallet_cliente = db.query(Wallet).filter(Wallet.usuario_id == pedido.customer_id).first()
    if not wallet_cliente:
        raise HTTPException(status_code=404, detail="Carteira do cliente não encontrada.")

    # Buscar o username do cliente (comprador)
    cliente = db.query(Usuario).filter(Usuario.id == pedido.customer_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Buscar o username do vendedor
    vendedor = db.query(Usuario).filter(Usuario.id == produto.CustomerID).first()
    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado.")

    # Liberar saldo congelado do vendedor
    wallet_vendedor.saldo_congelado -= pedido.preco_total
    wallet_vendedor.saldo_principal += pedido.preco_total

    # Atualizar o saldo congelado do cliente (diminuir o valor do saldo congelado)
    wallet_cliente.saldo_congelado -= pedido.preco_total

    # Converter o valor para float ou str antes de criar as transações
    valor_cliente = Decimal(-pedido.preco_total)
    valor_vendedor = Decimal(pedido.preco_total)

    # Registrar transação do cliente (saída de valor ao comprar)
    transacao_cliente = Transacao(
        usuario_id=wallet_cliente.usuario_id,
        msisdn=cliente.username,  # Usando o username do cliente
        valor=valor_cliente,  # Convertido para float
        referencia=f"Compra do produto {produto.nome}",
        status="sucesso",
        tipo="saida"
    )
    db.add(transacao_cliente)

    # Registrar transação do vendedor (entrada de valor ao vender)
    transacao_vendedor = Transacao(
        usuario_id=wallet_vendedor.usuario_id,
        msisdn=vendedor.username,  # Usando o username do vendedor
        valor=valor_vendedor,  # Convertido para float
        referencia=f"Venda do produto {produto.nome}",
        status="sucesso",
        tipo="entrada"
    )
    db.add(transacao_vendedor)

    db.commit()



def confirmar_pagamento_vendedor(db: Session, pedido_id: int, vendedor_id: int):
    pedido = db.query(Pedido).join(Produto).filter(Pedido.id == pedido_id, Produto.CustomerID == vendedor_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    if not pedido.recebido_pelo_cliente:
        raise HTTPException(status_code=400, detail="O cliente ainda não confirmou o recebimento.")

    pedido.aceito_pelo_vendedor = True
    pedido.status = "Pagamento Recebido"
    db.commit()

    # Se o pagamento e o recebimento forem confirmados, o pedido é finalizado
    if pedido.recebido_pelo_cliente and pedido.aceito_pelo_vendedor:
        pedido.status = "Concluído"
        db.commit()

        # Atualiza o estoque do produto
        produto = db.query(Produto).filter(Produto.id == pedido.produto_id).first()
        if produto:
            produto.quantidade_estoque -= pedido.quantidade  # Atualiza a quantidade em estoque
            if produto.quantidade_estoque <= 0:
                produto.ativo = False  # Desativa o produto se o estoque acabar
            db.commit()

        # Libera o saldo do vendedor
        liberar_saldo_vendedor(db, pedido)

    return {"mensagem": "Pagamento confirmado e pedido concluído."}





def obter_saldo_do_usuario(db: Session, user_id: int) -> Decimal:
    # Obter saldo atual do usuário na tabela 'wallet'
    wallet = db.query(Wallet).filter(Wallet.usuario_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet não encontrada")
    return wallet.saldo_principal

def obter_transacoes_por_usuario(db: Session, user_id: int):
    # Obter todas as transações do usuário
    return db.query(Transacao).filter(Transacao.usuario_id == user_id).all()

def registrar_log_discrepancia(user_id: int, saldo_atual:  int, saldo_calculado: int):
    # Registrar log de discrepância (simples log por enquanto, mas pode ser expandido para alertas)
    print(f"Discrepância detectada para o usuário {user_id}: saldo atual {saldo_atual}, saldo esperado {saldo_calculado}")
    
def verificar_integridade_saldo(db: Session, user_id: int):
    wallet = db.query(Wallet).filter(Wallet.usuario_id == user_id).first()
    if not wallet:
        raise Exception(f"Usuário {user_id} não possui uma wallet registrada.")
    
    saldo_atual1 = wallet.saldo_principal
    saldo_congelado = wallet.saldo_congelado
    saldo_atual = saldo_atual1 + saldo_congelado
    print(f"Saldo atual do usuário {user_id}: {saldo_atual}")

    # Somar todas as transações de entrada (status "sucesso" ou crédito)
    transacoes_entrada = db.query(Transacao).filter(
        Transacao.usuario_id == user_id, Transacao.status == "sucesso", Transacao.tipo == "entrada"
    ).all()
    total_entrada = sum([Decimal(transacao.valor) for transacao in transacoes_entrada])

    # Somar todas as transações de saída (status "sucesso" ou débito)
    transacoes_saida = db.query(Transacao).filter(
        Transacao.usuario_id == user_id, Transacao.status == "sucesso", Transacao.tipo == "saida"
    ).all()
    total_saida = sum([Decimal(transacao.valor) for transacao in transacoes_saida])

    # Calcular o saldo total (entradas - saídas) e garantir que o saldo não seja negativo
    saldo_calculado = max(total_entrada - total_saida, 0)

    print(f"Total de entradas: {total_entrada}")
    print(f"Total de saídas: {total_saida}")
    print(f"Saldo calculado para o usuário {user_id}: {saldo_calculado}")

    # Arredondar ambos os saldos para evitar problemas de precisão
    saldo_atual = round(saldo_atual, 2)
    saldo_calculado = round(saldo_calculado, 2)

    # Verificar se há discrepância
    if saldo_atual != saldo_calculado:
        raise Exception(f"Discrepância detectada para o usuário {user_id}: saldo atual {saldo_atual}, saldo esperado {saldo_calculado}")
    
    return {"msg": "Nenhuma discrepância detectada", "saldo_atual": saldo_atual, "saldo_calculado": saldo_calculado}
