"""empty message

Revision ID: 4489d6ed903e
Revises: 
Create Date: 2024-12-21 17:00:06.466474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4489d6ed903e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('image_url', sa.String(length=200), nullable=True),
    sa.Column('ingredients', sa.Text(), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('pantry_item',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('brand', sa.String(length=64), nullable=True),
    sa.Column('category', sa.String(length=64), nullable=False),
    sa.Column('used', sa.Boolean(), nullable=True),
    sa.Column('out_of_stock', sa.Boolean(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('expiration_date', sa.DateTime(), nullable=False),
    sa.Column('added_date', sa.DateTime(), nullable=True),
    sa.Column('calories', sa.Float(), nullable=True),
    sa.Column('nutrition_content', sa.Text(), nullable=True),
    sa.Column('image_path', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('pantry_item', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_pantry_item_name'), ['name'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pantry_item', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_pantry_item_name'))

    op.drop_table('pantry_item')
    op.drop_table('user')
    op.drop_table('recipe')
    # ### end Alembic commands ###