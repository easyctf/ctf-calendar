"""empty message

Revision ID: be302bbfe91c
Revises: 95e27ab5ca98
Create Date: 2016-06-10 12:12:54.792950

"""

# revision identifiers, used by Alembic.
revision = 'be302bbfe91c'
down_revision = '95e27ab5ca98'

from alembic import op
import sqlalchemy as sa


def upgrade():
### commands auto generated by Alembic - please adjust! ###
    op.add_column('events', sa.Column('owner', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_events_owner'), 'events', ['owner'], unique=False)
    op.create_foreign_key(None, 'events', 'users', ['owner'], ['id'])
    ### end Alembic commands ###


def downgrade():
### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'events', type_='foreignkey')
    op.drop_index(op.f('ix_events_owner'), table_name='events')
    op.drop_column('events', 'owner')
    ### end Alembic commands ###
