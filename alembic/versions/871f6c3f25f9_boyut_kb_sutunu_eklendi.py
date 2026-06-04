"""boyut_kb sutunu eklendi

Revision ID: 871f6c3f25f9
Revises: 4dc549cbf683
Create Date: 2026-06-03 19:13:13.330583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '871f6c3f25f9'
down_revision: Union[str, Sequence[str], None] = '4dc549cbf683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('belgeler', sa.Column('boyut_kb', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('belgeler', 'boyut_kb')
