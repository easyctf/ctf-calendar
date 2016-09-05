"""Add password reset fields.

Revision ID: 7905cec750a2
Revises: d25be15cb75d
Create Date: 2016-09-04 00:53:58.969972

"""

# revision identifiers, used by Alembic.
revision = '7905cec750a2'
down_revision = 'd25be15cb75d'

from alembic import op
import sqlalchemy as sa


def upgrade():
### commands auto generated by Alembic - please adjust! ###
    op.create_table('password_reset_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('token', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('expire', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
### commands auto generated by Alembic - please adjust! ###
    op.drop_table('password_reset_token')
    ### end Alembic commands ###