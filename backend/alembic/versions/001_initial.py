"""Initial schema for MoodAtlas

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-07 12:00:00.000000

Creates the foundational database schema with two main tables:
- country_mood: Stores daily mood snapshots per country
- mood_spike: Tracks significant mood changes/anomalies
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    
    # ── country_mood table ──────────────────────────────────────────
    op.create_table(
        'country_mood',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('country_code', sa.String(length=3), nullable=False),
        sa.Column('country_name', sa.String(length=120), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Mood metrics
        sa.Column('mood_score', sa.Float(), nullable=False, comment='Mood value from -1.0 (negative) to 1.0 (positive)'),
        sa.Column('mood_label', sa.String(length=20), nullable=False, comment='Happy | Calm | Sad | Angry | Anxious'),
        sa.Column('color_code', sa.String(length=7), nullable=False, comment='Hex color code for visualization'),
        
        # Audio features from Last.fm
        sa.Column('valence', sa.Float(), nullable=True, comment='Musical positiveness (0-1)'),
        sa.Column('energy', sa.Float(), nullable=True, comment='Musical intensity (0-1)'),
        sa.Column('danceability', sa.Float(), nullable=True, comment='Danceability measure (0-1)'),
        sa.Column('acousticness', sa.Float(), nullable=True, comment='Acoustic vs electronic (0-1)'),
        
        # Supplementary data
        sa.Column('top_genre', sa.String(length=60), nullable=True, comment='Most popular genre'),
        sa.Column('top_track', sa.String(length=200), nullable=True, comment='Most popular track'),
        sa.Column('news_sentiment', sa.Float(), nullable=True, comment='News sentiment score (-1 to 1)'),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('country_code', 'date', name='uq_country_date'),
    )
    
    # Indexes for country_mood
    op.create_index('idx_country_mood_code', 'country_mood', ['country_code'])
    op.create_index('idx_country_mood_date', 'country_mood', ['date'])
    op.create_index('idx_country_mood_code_date', 'country_mood', ['country_code', 'date'])
    
    # ── mood_spike table ────────────────────────────────────────────
    op.create_table(
        'mood_spike',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('country_code', sa.String(length=3), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('previous_label', sa.String(length=20), nullable=False),
        sa.Column('new_label', sa.String(length=20), nullable=False),
        sa.Column('delta', sa.Float(), nullable=False, comment='Magnitude of mood change'),
        sa.Column('reason', sa.Text(), nullable=True, comment='Detected cause of spike'),
        
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Indexes for mood_spike
    op.create_index('idx_mood_spike_code', 'mood_spike', ['country_code'])
    op.create_index('idx_mood_spike_detected', 'mood_spike', ['detected_at'])
    op.create_index('idx_mood_spike_code_detected', 'mood_spike', ['country_code', 'detected_at'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('idx_mood_spike_code_detected', table_name='mood_spike')
    op.drop_index('idx_mood_spike_detected', table_name='mood_spike')
    op.drop_index('idx_mood_spike_code', table_name='mood_spike')
    op.drop_table('mood_spike')
    
    op.drop_index('idx_country_mood_code_date', table_name='country_mood')
    op.drop_index('idx_country_mood_date', table_name='country_mood')
    op.drop_index('idx_country_mood_code', table_name='country_mood')
    op.drop_table('country_mood')
