"""alteracao de infousuario

Revision ID: 24357c2871d6
Revises: 545e901a1fac
Create Date: 2024-11-25 08:30:26.616016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '24357c2871d6'
down_revision: Union[str, None] = '545e901a1fac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_messages_id', table_name='messages')
    op.drop_table('messages')
    op.drop_table('produto_likes')
    op.drop_index('ix_comentario_comentarioID', table_name='comentario')
    op.drop_table('comentario')
    op.drop_index('google_id', table_name='usuarios')
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_index('ix_usuarios_id', table_name='usuarios')
    op.drop_index('ix_usuarios_username', table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index('ix_status_id', table_name='status')
    op.drop_table('status')
    op.drop_index('ix_seguidores_id', table_name='seguidores')
    op.drop_table('seguidores')
    op.drop_index('ix_pesquisas_id', table_name='pesquisas')
    op.drop_index('ix_pesquisas_termo_pesquisa', table_name='pesquisas')
    op.drop_table('pesquisas')
    op.drop_index('ix_publicacoes_id', table_name='publicacoes')
    op.drop_table('publicacoes')
    op.drop_index('ix_info_usuario_id', table_name='info_usuario')
    op.drop_table('info_usuario')
    op.drop_index('ix_transacoes_id', table_name='transacoes')
    op.drop_table('transacoes')
    op.drop_index('ix_anuncio_id', table_name='anuncio')
    op.drop_index('produto_id', table_name='anuncio')
    op.drop_table('anuncio')
    op.drop_index('ix_notificacoes_id', table_name='notificacoes')
    op.drop_table('notificacoes')
    op.drop_index('ix_pedido_id', table_name='pedido')
    op.drop_table('pedido')
    op.drop_index('email', table_name='admin')
    op.drop_index('ix_admin_id', table_name='admin')
    op.drop_table('admin')
    op.drop_index('ix_wallet_id', table_name='wallet')
    op.drop_index('usuario_id', table_name='wallet')
    op.drop_table('wallet')
    op.drop_index('ix_endereco_envio_id', table_name='endereco_envio')
    op.drop_table('endereco_envio')
    op.drop_index('ix_produto_id', table_name='produto')
    op.drop_index('ix_produto_slug', table_name='produto')
    op.drop_table('produto')
    op.drop_index('ix_denunciaProduto_id', table_name='denunciaProduto')
    op.drop_table('denunciaProduto')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('denunciaProduto',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('produtoID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('CustomerID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('motivo', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('descricao', mysql.TEXT(), nullable=True),
    sa.Column('data_denuncia', mysql.DATETIME(), nullable=True),
    sa.Column('status', mysql.VARCHAR(length=350), nullable=True),
    sa.ForeignKeyConstraint(['CustomerID'], ['usuarios.id'], name='denunciaProduto_ibfk_2'),
    sa.ForeignKeyConstraint(['produtoID'], ['produto.id'], name='denunciaProduto_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_denunciaProduto_id', 'denunciaProduto', ['id'], unique=False)
    op.create_table('produto',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nome', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('capa', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('fotos', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('preco', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.Column('quantidade_estoque', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('estado', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('provincia', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('distrito', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('revisao', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('disponiblidade', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('descricao', mysql.TEXT(), nullable=True),
    sa.Column('categoria', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('detalhes', mysql.VARCHAR(length=1000), nullable=True),
    sa.Column('tipo', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('visualizacoes', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ativo', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('CustomerID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('likes', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('data_publicacao', mysql.DATETIME(), nullable=True),
    sa.Column('slug', mysql.VARCHAR(length=250), nullable=True),
    sa.ForeignKeyConstraint(['CustomerID'], ['usuarios.id'], name='produto_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_produto_slug', 'produto', ['slug'], unique=True)
    op.create_index('ix_produto_id', 'produto', ['id'], unique=False)
    op.create_table('endereco_envio',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('CustomerID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('pedidoID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('endereco_line1', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('endereco_line2', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('cidade', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('estado', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('codigo_postal', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('pais', mysql.VARCHAR(length=350), nullable=True),
    sa.ForeignKeyConstraint(['CustomerID'], ['usuarios.id'], name='endereco_envio_ibfk_1'),
    sa.ForeignKeyConstraint(['pedidoID'], ['pedido.id'], name='endereco_envio_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_endereco_envio_id', 'endereco_envio', ['id'], unique=False)
    op.create_table('wallet',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('saldo_principal', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.Column('saldo_congelado', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.Column('bonus', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='wallet_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('usuario_id', 'wallet', ['usuario_id'], unique=True)
    op.create_index('ix_wallet_id', 'wallet', ['id'], unique=False)
    op.create_table('admin',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nome', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('senha', mysql.VARCHAR(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_admin_id', 'admin', ['id'], unique=False)
    op.create_index('email', 'admin', ['email'], unique=True)
    op.create_table('pedido',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('customer_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('produto_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('quantidade', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('preco_unitario', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.Column('preco_total', mysql.DECIMAL(precision=10, scale=0), nullable=True),
    sa.Column('data_pedido', mysql.DATETIME(), nullable=True),
    sa.Column('status', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('aceito_pelo_vendedor', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('recebido_pelo_cliente', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('data_aceite', mysql.DATETIME(), nullable=True),
    sa.Column('data_envio', mysql.DATETIME(), nullable=True),
    sa.Column('data_entrega', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['usuarios.id'], name='pedido_ibfk_1'),
    sa.ForeignKeyConstraint(['produto_id'], ['produto.id'], name='pedido_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_pedido_id', 'pedido', ['id'], unique=False)
    op.create_table('notificacoes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('mensagem', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('data', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='notificacoes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_notificacoes_id', 'notificacoes', ['id'], unique=False)
    op.create_table('anuncio',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('titulo', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('descricao', mysql.TEXT(), nullable=True),
    sa.Column('tipo_anuncio', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('produto_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('promovido_em', mysql.DATETIME(), nullable=True),
    sa.Column('expira_em', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['produto_id'], ['produto.id'], name='anuncio_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('produto_id', 'anuncio', ['produto_id'], unique=True)
    op.create_index('ix_anuncio_id', 'anuncio', ['id'], unique=False)
    op.create_table('transacoes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('msisdn', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('valor', mysql.DECIMAL(precision=10, scale=0), nullable=False),
    sa.Column('referencia', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('status', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('data_hora', mysql.DATETIME(), nullable=True),
    sa.Column('tipo', mysql.VARCHAR(length=20), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='transacoes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_transacoes_id', 'transacoes', ['id'], unique=False)
    op.create_table('info_usuario',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('foto_retrato', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('foto_bi_frente', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('foto_bi_verso', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('provincia', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('distrito', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('data_nascimento', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('localizacao', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('estado', mysql.VARCHAR(length=350), nullable=True),
    sa.Column('contacto', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('sexo', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('nacionalidade', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('bairro', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('revisao', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='info_usuario_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_info_usuario_id', 'info_usuario', ['id'], unique=False)
    op.create_table('publicacoes',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('conteudo', mysql.VARCHAR(length=250), nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='publicacoes_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_publicacoes_id', 'publicacoes', ['id'], unique=False)
    op.create_table('pesquisas',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('termo_pesquisa', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('categoria_pesquisa', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('data_pesquisa', mysql.DATETIME(), nullable=True),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='pesquisas_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_pesquisas_termo_pesquisa', 'pesquisas', ['termo_pesquisa'], unique=False)
    op.create_index('ix_pesquisas_id', 'pesquisas', ['id'], unique=False)
    op.create_table('seguidores',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('seguidor_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['seguidor_id'], ['usuarios.id'], name='seguidores_ibfk_2'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='seguidores_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_seguidores_id', 'seguidores', ['id'], unique=False)
    op.create_table('status',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('conteudo', mysql.TEXT(), nullable=True),
    sa.Column('imagem_url', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('expira_em', mysql.DATETIME(), nullable=False),
    sa.Column('custo_total', mysql.DECIMAL(precision=10, scale=0), nullable=False),
    sa.Column('visualizacoes', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='status_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_status_id', 'status', ['id'], unique=False)
    op.create_table('usuarios',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('nome', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('senha', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('google_id', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('tipo', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('foto_perfil', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('ativo', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('conta_pro', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('limite_diario_publicacoes', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('data_cadastro', mysql.DATETIME(), nullable=True),
    sa.Column('data_ativacao_pro', mysql.DATETIME(), nullable=True),
    sa.Column('revisao', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_usuarios_username', 'usuarios', ['username'], unique=True)
    op.create_index('ix_usuarios_id', 'usuarios', ['id'], unique=False)
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)
    op.create_index('google_id', 'usuarios', ['google_id'], unique=True)
    op.create_table('comentario',
    sa.Column('comentarioID', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('produtoID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('CustomerID', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('comentario', mysql.TEXT(), nullable=True),
    sa.Column('data_comentario', mysql.DATETIME(), nullable=True),
    sa.Column('avaliacao', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['CustomerID'], ['usuarios.id'], name='comentario_ibfk_2'),
    sa.ForeignKeyConstraint(['produtoID'], ['produto.id'], name='comentario_ibfk_1'),
    sa.PrimaryKeyConstraint('comentarioID'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_comentario_comentarioID', 'comentario', ['comentarioID'], unique=False)
    op.create_table('produto_likes',
    sa.Column('produto_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('usuario_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['produto_id'], ['produto.id'], name='produto_likes_ibfk_1'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], name='produto_likes_ibfk_2'),
    sa.PrimaryKeyConstraint('produto_id', 'usuario_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('messages',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('sender_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('receiver_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('content', mysql.TEXT(), nullable=True),
    sa.Column('message_type', mysql.ENUM('TEXT', 'IMAGE', 'PDF', 'AUDIO', 'VIDEO'), nullable=False),
    sa.Column('file_url', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('file_name', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('file_size', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), server_default=sa.text('(now())'), nullable=True),
    sa.Column('is_read', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['receiver_id'], ['usuarios.id'], name='messages_ibfk_2'),
    sa.ForeignKeyConstraint(['sender_id'], ['usuarios.id'], name='messages_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    # ### end Alembic commands ###
