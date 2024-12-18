"""Revisão final

Revision ID: f3354ad1d395
Revises: cf2c58fec219
Create Date: 2024-12-13 15:55:03.650335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3354ad1d395'
down_revision: Union[str, None] = 'cf2c58fec219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuarios', sa.Column('identificador_unico', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_usuarios_identificador_unico'), 'usuarios', ['identificador_unico'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_usuarios_identificador_unico'), table_name='usuarios')
    op.drop_column('usuarios', 'identificador_unico')
    # ### end Alembic commands ###
