"""create indexes on frequently queried columns"""

from alembic import op
import sqlalchemy as sa

revision = '20240607_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_items_name', 'items', ['name'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade():
    op.drop_index('ix_audit_logs_timestamp', table_name='audit_logs')
    op.drop_index('ix_items_name', table_name='items')
