"""add totp secret to user"""

from alembic import op
import sqlalchemy as sa

revision = '20240607_add_totp'
down_revision = '20240606_add_dept_cat'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('totp_secret', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'totp_secret')
