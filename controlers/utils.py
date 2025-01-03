from models import Log,Produto,Usuario
from sqlalchemy.orm import Session
from datetime import datetime
import random





def registrar_acao_com_categoria(
    db: Session,
    usuario_id: int,
    tipo_acao: str,
    produto_id: int,
    entidade: str,
    detalhes: dict
):
    """
    Registra a ação de um usuário, associando à categoria do produto.
    """
    
    # Recupera a categoria do produto
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise ValueError("Produto não encontrado ao registrar ação.")
    
    # Adiciona a categoria nos detalhes
    detalhes["categoria"] = produto.categoria

    # Registra o log
    log = Log(
        usuario_id=usuario_id,
        tipo_acao=tipo_acao,
        entidade=entidade,
        detalhes=detalhes,
        data_hora=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log

def gerar_identificador_unico(db: Session):
    """
    Gera um identificador único no formato "sk-123456789".
    Verifica se já existe no banco antes de retornar.
    """
    while True:
        identificador = f"sk-{random.randint(100000000, 999999999)}"
        if not db.query(Usuario).filter(Usuario.identificador_unico == identificador).first():
            return identificador