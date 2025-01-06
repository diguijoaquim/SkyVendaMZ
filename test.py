from sqlalchemy import create_engine, inspect

def obter_tipo_colunas():
    # Conectar ao banco de dados
    DATABASE_URL = "postgresql://postgres:uCUCjSkArNRiteSTDrxMuwyldXGKeTQO@junction.proxy.rlwy.net:42999/railway"
    engine = create_engine(DATABASE_URL)
    
    # Usando o método inspect para inspecionar a tabela
    inspector = inspect(engine)
    
    # Nome da tabela que você quer inspecionar
    nome_da_tabela = "pedido"  # Altere para o nome da sua tabela
    
    # Obter informações sobre as colunas da tabela
    colunas = inspector.get_columns(nome_da_tabela)
    
    # Imprimir o tipo de cada coluna
    for coluna in colunas:
        print(f"Coluna: {coluna['name']}, Tipo: {coluna['type']}")

# Chame a função
obter_tipo_colunas()
