"""Add production query indexes

Revision ID: f4a2c9d8e1b3
Revises: 9d3c2f1a8b7e
Create Date: 2026-06-22 00:00:00.000000

"""
from alembic import op


revision = 'f4a2c9d8e1b3'
down_revision = '9d3c2f1a8b7e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cost_entry', schema=None) as batch_op:
        batch_op.create_index(
            'ix_cost_project_void_date',
            ['project_id', 'is_void', 'date'],
            unique=False,
        )
        batch_op.create_index(
            'ix_cost_void_date',
            ['is_void', 'date'],
            unique=False,
        )
        batch_op.create_index(
            'ix_cost_project_type_date',
            ['project_id', 'cost_type', 'date'],
            unique=False,
        )

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.create_index(
            'ix_project_status_void',
            ['status', 'is_void'],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_index('ix_project_status_void')

    with op.batch_alter_table('cost_entry', schema=None) as batch_op:
        batch_op.drop_index('ix_cost_project_type_date')
        batch_op.drop_index('ix_cost_void_date')
        batch_op.drop_index('ix_cost_project_void_date')
