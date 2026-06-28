"""Add users and team ownership.

Revision ID: 20260628_0002
Revises: 20260618_0001
Create Date: 2026-06-28
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260628_0002"
down_revision: str | None = "20260618_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    with op.batch_alter_table("teams") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_teams_owner_id_users", "users", ["owner_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("teams") as batch_op:
        batch_op.drop_constraint("fk_teams_owner_id_users", type_="foreignkey")
        batch_op.drop_column("owner_id")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
