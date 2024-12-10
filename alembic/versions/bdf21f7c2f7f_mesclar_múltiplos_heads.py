"""Mesclar múltiplos heads

Revision ID: bdf21f7c2f7f
Revises: 0fecf9eb16c5, 24357c2871d6, daf1ac977e98
Create Date: 2024-12-10 09:57:21.090528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdf21f7c2f7f'
down_revision: Union[str, None] = ('0fecf9eb16c5', '24357c2871d6', 'daf1ac977e98')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
