"""Add news_headlines and news_summary columns

Revision ID: 002_add_news_fields
Revises: 001_initial
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_news_fields'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add news_headlines column (stores JSON array as text)
    op.add_column('country_mood', sa.Column('news_headlines', sa.Text(), nullable=True))
    
    # Add news_summary column (AI-generated summary)
    op.add_column('country_mood', sa.Column('news_summary', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('country_mood', 'news_summary')
    op.drop_column('country_mood', 'news_headlines')
