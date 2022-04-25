"""added PAW info model

Revision ID: a4e1e662c62f
Revises: a404a3183228
Create Date: 2022-04-20 12:43:18.645536

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4e1e662c62f'
down_revision = 'a404a3183228'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('paw_info',
    sa.Column('variant_id', sa.String(length=15), nullable=False),
    sa.Column('info', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('variant_id')
    )
    op.create_index(op.f('ix_paw_info_variant_id'), 'paw_info', ['variant_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_paw_info_variant_id'), table_name='paw_info')
    op.drop_table('paw_info')
    # ### end Alembic commands ###
