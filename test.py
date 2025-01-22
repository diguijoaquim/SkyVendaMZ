import psycopg2

def excluir_criar_tabela_pedido():
    # URL de conexão ao banco de dados
    DATABASE_URL = "postgresql://postgres:uCUCjSkArNRiteSTDrxMuwyldXGKeTQO@junction.proxy.rlwy.net:42999/railway"
    
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("Conexão com o banco de dados estabelecida com sucesso!")

        # Comando SQL para excluir a tabela 'pedido', caso exista
        excluir_tabela_pedido = "DROP TABLE IF EXISTS pedido CASCADE;"
        
        # Comando SQL para criar a tabela 'pedido'
        criar_tabela_pedido = """
            CREATE TABLE pedido (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                produto_id INTEGER NOT NULL REFERENCES produto(id) ON DELETE CASCADE,
                quantidade INTEGER NOT NULL,
                preco_total DECIMAL,
                status_visivel_comprador BOOLEAN DEFAULT FALSE,
                status_visivel_vendedor BOOLEAN DEFAULT FALSE,
                data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(350),
                aceito_pelo_vendedor BOOLEAN DEFAULT FALSE,
                tipo VARCHAR(20),
                recebido_pelo_cliente BOOLEAN DEFAULT FALSE,
                data_aceite TIMESTAMP,
                data_envio TIMESTAMP,
                data_entrega TIMESTAMP,
                data_confirmacao_recebimento TIMESTAMP,
                data_limite_confirmacao TIMESTAMP
            );
        """

        # Excluindo a tabela, se existir
        print("Excluindo a tabela 'pedido', caso exista...")
        cursor.execute(excluir_tabela_pedido)

        # Criando a tabela
        print("Criando a tabela 'pedido'...")
        cursor.execute(criar_tabela_pedido)

        # Commit para salvar as mudanças no banco de dados
        conn.commit()
        print("Tabela 'pedido' criada com sucesso!")

    except Exception as e:
        print(f"Erro ao excluir e criar a tabela 'pedido': {e}")
    
    finally:
        # Fechar o cursor e a conexão com o banco de dados
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Conexão com o banco de dados fechada.")

# Chamar a função
excluir_criar_tabela_pedido()
