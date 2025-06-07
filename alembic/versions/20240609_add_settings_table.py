"""add settings table"""

from alembic import op
import sqlalchemy as sa

revision = '20240609_add_settings'
down_revision = '20240608_remove_totp'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('tenant_id', sa.Integer, sa.ForeignKey('tenants.id')),
        sa.Column('key', sa.String, nullable=False),
        sa.Column('value', sa.String, nullable=False),
        sa.UniqueConstraint('tenant_id', 'key', name='uix_tenant_key'),
    )


def downgrade():
    op.drop_table('settings')

