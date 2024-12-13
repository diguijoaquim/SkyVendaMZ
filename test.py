from sqlalchemy.orm import Session
from models import Usuario
from database import SessionLocal
import random

def gerar_identificador():
    return f"sk-{random.randint(100000000, 999999999)}"

def atualizar_identificadores(db: Session):
    usuarios_sem_identificador = db.query(Usuario).filter(Usuario.identificador_unico.is_(None)).all()

    for usuario in usuarios_sem_identificador:
        while True:
            identificador = gerar_identificador()
            # Verifica se o identificador já existe no banco
            if not db.query(Usuario).filter(Usuario.identificador_unico == identificador).first():
                usuario.identificador_unico = identificador
                break

    db.commit()
    print(f"{len(usuarios_sem_identificador)} usuários atualizados com identificadores únicos!")

# Executa o script
if __name__ == "__main__":
    db = SessionLocal()
    try:
        atualizar_identificadores(db)
    finally:
        db.close()
