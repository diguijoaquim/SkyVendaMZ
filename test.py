import psycopg2

def excluir_criar_tabelas():
    # Dados de conexão
    DATABASE_URL = "postgresql://postgres:uCUCjSkArNRiteSTDrxMuwyldXGKeTQO@junction.proxy.rlwy.net:42999/railway"
    
    try:
        # Conectar ao banco de dados PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Comandos SQL para excluir as tabelas, caso existam
        excluir_tabela_pedido = "DROP TABLE IF EXISTS pedido CASCADE;"
        excluir_tabela_anuncio = "DROP TABLE IF EXISTS anuncio CASCADE;"
        
        # Comando SQL para criar a tabela 'pedido'
        criar_tabela_pedido = """
            CREATE TABLE pedido (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
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
                FOREIGN KEY (customer_id) REFERENCES usuarios(id),
                FOREIGN KEY (produto_id) REFERENCES produto(id)
            );
        """

        # Comando SQL para criar a tabela 'anuncio'
        criar_tabela_anuncio = """
            CREATE TABLE anuncio (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(350),
                descricao TEXT,
                tipo_anuncio VARCHAR(350),
                produto_id INTEGER UNIQUE,
                promovido_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expira_em TIMESTAMP,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY (produto_id) REFERENCES produto(id)
            );
        """

        # Executar os comandos SQL
        cursor.execute(excluir_tabela_pedido)
        cursor.execute(excluir_tabela_anuncio)
        cursor.execute(criar_tabela_pedido)
        cursor.execute(criar_tabela_anuncio)

        # Commit para garantir que as mudanças sejam salvas no banco de dados
        conn.commit()

        print("Tabelas 'pedido' e 'anuncio' excluídas e criadas com sucesso!")

    except Exception as e:
        print(f"Erro ao excluir e criar as tabelas: {e}")
    
    finally:
        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()

# Chame a função
excluir_criar_tabelas()
