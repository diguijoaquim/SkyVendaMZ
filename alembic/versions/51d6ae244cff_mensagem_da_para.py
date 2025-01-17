"""Mensagem da para

Revision ID: 51d6ae244cff
Revises: b715e89ae4b8
Create Date: 2025-01-06 14:53:39.029394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51d6ae244cff'
down_revision: Union[str, None] = 'b715e89ae4b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('pedido', 'status_visivel_comprador',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('pedido', 'status_visivel_vendedor',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.Boolean(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('pedido', 'status_visivel_vendedor',
               existing_type=sa.Boolean(),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    op.alter_column('pedido', 'status_visivel_comprador',
               existing_type=sa.Boolean(),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
    # ### end Alembic commands ###
