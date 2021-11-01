"""empty message

Revision ID: 3b06d1ab4b15
Revises: 
Create Date: 2021-11-01 16:36:41.727700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b06d1ab4b15'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dialogue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('users_ids', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('msg', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('viewed', sa.Boolean(), nullable=False),
    sa.Column('dialogue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['dialogue_id'], ['dialogue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    op.drop_table('dialogue')
    # ### end Alembic commands ###