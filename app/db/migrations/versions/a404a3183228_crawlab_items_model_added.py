"""Crawlab items model added

Revision ID: a404a3183228
Revises: bbb48220c3fa
Create Date: 2022-02-25 16:27:59.428049

"""
from alembic import op
import sqlalchemy as sa
import ormar


# revision identifiers, used by Alembic.
revision = 'a404a3183228'
down_revision = 'bbb48220c3fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('crawlab_info',
    sa.Column('ean', sa.String(length=13), nullable=False),
    sa.Column('info', sa.JSON(), nullable=False),
    sa.Column('task_id', ormar.fields.sqlalchemy_uuid.CHAR(32), nullable=False),
    sa.PrimaryKeyConstraint('ean')
    )
    op.create_index(op.f('ix_crawlab_info_ean'), 'crawlab_info', ['ean'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_crawlab_info_ean'), table_name='crawlab_info')
    op.drop_table('crawlab_info')
    # ### end Alembic commands ###
