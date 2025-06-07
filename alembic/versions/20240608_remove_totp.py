"""remove totp column"""

from alembic import op
import sqlalchemy as sa

revision = "20240608_remove_totp"
down_revision = "20240607_add_totp"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "totp_secret")


def downgrade():
    op.add_column("users", sa.Column("totp_secret", sa.String(), nullable=True))
