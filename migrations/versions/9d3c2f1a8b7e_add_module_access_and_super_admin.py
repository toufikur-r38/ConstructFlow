"""Add module access and super admin

Revision ID: 9d3c2f1a8b7e
Revises: 7c4a9b2d1e6f
Create Date: 2026-06-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '9d3c2f1a8b7e'
down_revision = '7c4a9b2d1e6f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_super_admin', sa.Boolean(), nullable=False, server_default=sa.false())
        )

    op.create_table(
        'user_module',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'module_name', name='uq_user_module_access')
    )
    with op.batch_alter_table('user_module', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_module_module_name'), ['module_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_module_user_id'), ['user_id'], unique=False)

    user_table = sa.table(
        'user',
        sa.column('id', sa.Integer),
        sa.column('username', sa.String),
        sa.column('is_super_admin', sa.Boolean),
    )
    user_module_table = sa.table(
        'user_module',
        sa.column('user_id', sa.Integer),
        sa.column('module_name', sa.String),
    )

    connection = op.get_bind()
    existing_users = connection.execute(sa.select(user_table.c.id)).fetchall()
    if existing_users:
        connection.execute(
            user_module_table.insert(),
            [{'user_id': row.id, 'module_name': 'construction'} for row in existing_users],
        )

    connection.execute(
        user_table.update()
        .where(user_table.c.username == 'admin')
        .values(is_super_admin=True)
    )

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_super_admin', server_default=None)


def downgrade():
    with op.batch_alter_table('user_module', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_module_user_id'))
        batch_op.drop_index(batch_op.f('ix_user_module_module_name'))

    op.drop_table('user_module')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_super_admin')
