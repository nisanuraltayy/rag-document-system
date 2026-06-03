"""ilk migration: belgeler tablosu

Revision ID: 4dc549cbf683
Revises: 
Create Date: 2026-06-03 19:07:28.950584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dc549cbf683'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'belgeler',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dosya_adi', sa.String(length=255), nullable=False),
        sa.Column('tur', sa.String(length=50), nullable=False),
        sa.Column('parca_sayisi', sa.Integer(), nullable=False),
        sa.Column('yukleme_tarihi', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_belgeler_id'), 'belgeler', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_belgeler_id'), table_name='belgeler')
    op.drop_table('belgeler')
