"""Create person table.

Revision ID: 357e5326cdf1
Revises:
Create Date: 2022-08-26 17:45:49.627169
"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '357e5326cdf1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade."""
    op.create_table(
        'person',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('second_name', sa.String(50), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade."""
    op.drop_table('person')
