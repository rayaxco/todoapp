"""create phone number on user column

Revision ID: ab1fd283fd4a
Revises: 
Create Date: 2025-12-07 20:39:59.557912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab1fd283fd4a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String(16),nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
