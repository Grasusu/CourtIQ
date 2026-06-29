"""Add upload jobs.

Revision ID: 20260629_0003
Revises: 20260628_0002
Create Date: 2026-06-29
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260629_0003"
down_revision: str | None = "20260628_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "upload_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("rows_processed", sa.Integer(), nullable=False),
        sa.Column("games_created", sa.Integer(), nullable=False),
        sa.Column("players_created", sa.Integer(), nullable=False),
        sa.Column("stats_created", sa.Integer(), nullable=False),
        sa.Column("stats_updated", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_upload_jobs_owner_id"), "upload_jobs", ["owner_id"], unique=False)
    op.create_index(op.f("ix_upload_jobs_team_id"), "upload_jobs", ["team_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_upload_jobs_team_id"), table_name="upload_jobs")
    op.drop_index(op.f("ix_upload_jobs_owner_id"), table_name="upload_jobs")
    op.drop_table("upload_jobs")
