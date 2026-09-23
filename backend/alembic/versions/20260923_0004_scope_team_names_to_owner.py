"""Scope team names to their owner.

Revision ID: 20260923_0004
Revises: 20260629_0003
Create Date: 2026-09-23
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260923_0004"
down_revision: str | None = "20260629_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    existing_constraint = "teams_name_key" if dialect == "postgresql" else "uq_teams_name"
    with op.batch_alter_table(
        "teams",
        naming_convention={"uq": "uq_%(table_name)s_%(column_0_name)s"},
    ) as batch_op:
        batch_op.drop_constraint(existing_constraint, type_="unique")
        batch_op.create_unique_constraint("uq_team_owner_name", ["owner_id", "name"])


def downgrade() -> None:
    with op.batch_alter_table("teams") as batch_op:
        batch_op.drop_constraint("uq_team_owner_name", type_="unique")
        batch_op.create_unique_constraint("uq_teams_name", ["name"])
