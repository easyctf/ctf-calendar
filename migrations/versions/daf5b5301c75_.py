"""empty message

Revision ID: daf5b5301c75
Revises: f79ba2365689
Create Date: 2016-06-30 10:08:05.129124

"""

# revision identifiers, used by Alembic.
revision = 'daf5b5301c75'
down_revision = 'f79ba2365689'

import sqlalchemy as sa
from alembic import op


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('eventvotes', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('eventvote_user_event_uc', 'eventvotes', ['user_id', 'event_id'])
    op.create_foreign_key('eventvote_user_id_fk', 'eventvotes', 'users', ['user_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('eventvote_user_id_fk', 'eventvotes', type_='foreignkey')
    op.drop_constraint('eventvote_user_event_uc', 'eventvotes', type_='unique')
    op.drop_column('eventvotes', 'user_id')
    ### end Alembic commands ###