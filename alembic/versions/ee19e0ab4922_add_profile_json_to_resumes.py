"""add profile_json to resumes

Revision ID: ee19e0ab4922
Revises: 
Create Date: 2026-08-29 23:04:44.372663
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'ee19e0ab4922'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('resumes', sa.Column('profile_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('resumes', 'profile_json')
