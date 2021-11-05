"""empty message

Revision ID: 59b8a3bcded5
Revises: 
Create Date: 2021-11-04 16:46:27.817847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59b8a3bcded5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dialogue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('users_ids', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('users_ids')
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
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.Integer(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('message')
    op.drop_table('dialogue')
    # ### end Alembic commands ###