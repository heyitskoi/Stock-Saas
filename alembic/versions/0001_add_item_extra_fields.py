"""add item extra fields"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('items', sa.Column('min_par', sa.Integer(), server_default='0'))
    op.add_column('items', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('items', sa.Column('category_id', sa.Integer(), nullable=True))
    op.add_column('items', sa.Column('stock_code', sa.String(), nullable=True))
    op.add_column('items', sa.Column('status', sa.String(), nullable=True))
    op.alter_column('items', 'min_par', server_default=None)


def downgrade():
    op.drop_column('items', 'status')
    op.drop_column('items', 'stock_code')
    op.drop_column('items', 'category_id')
    op.drop_column('items', 'department_id')
    op.drop_column('items', 'min_par')
