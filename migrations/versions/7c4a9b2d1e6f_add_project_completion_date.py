"""Add project completion date

Revision ID: 7c4a9b2d1e6f
Revises: b2e4a76b9856
Create Date: 2026-06-07 03:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c4a9b2d1e6f'
down_revision = 'b2e4a76b9856'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completion_date', sa.Date(), nullable=True))
        batch_op.create_index(batch_op.f('ix_project_completion_date'), ['completion_date'], unique=False)


def downgrade():
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_completion_date'))
        batch_op.drop_column('completion_date')
