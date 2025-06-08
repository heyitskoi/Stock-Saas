"""add email column to users"""

from alembic import op
import sqlalchemy as sa

revision = "20240609_add_email"
down_revision = "20240608_remove_totp"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "email")

