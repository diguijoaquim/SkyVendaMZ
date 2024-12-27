from sqlalchemy import create_engine, text

# Substitua pela URL de conexão com o banco de dados
DATABASE_URL = "postgresql://postgres:gQJIzVbyZEDacKjrhTraoyGvCEcAAlvi@junction.proxy.rlwy.net:37958/railway"  # Exemplo para PostgreSQL

# Crie o engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Execute o comando DROP TABLE
with engine.connect() as connection:
    try:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        print("Tabela 'alembic_version' removida com sucesso!")
    except Exception as e:
        print(f"Erro ao remover a tabela: {e}")

