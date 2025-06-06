"""create departments and categories tables"""

from alembic import op
import sqlalchemy as sa

revision = '20240606_add_dept_cat'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('icon', sa.String, nullable=True),
    )
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=False),
        sa.Column('icon', sa.String, nullable=True),
    )
    op.add_column('items', sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id'), nullable=True))
    op.add_column('items', sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id'), nullable=True))


def downgrade():
    op.drop_column('items', 'category_id')
    op.drop_column('items', 'department_id')
    op.drop_table('categories')
    op.drop_table('departments')
