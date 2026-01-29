"""add_body_html_to_email

Revision ID: 5240e1f7c552
Revises: bb89e3ec0cdf
Create Date: 2026-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5240e1f7c552'
down_revision = 'ae2c30622bdb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('emails', sa.Column('body_html', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('emails', 'body_html')
