"""Add basic driver profiles for later trip assignment."""

from alembic import op
import sqlalchemy as sa

revision = "0003_create_drivers"
down_revision = "0002_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "drivers",
        sa.Column("driver_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("license_number", sa.String(length=40), nullable=False),
        sa.Column("license_expiry", sa.Date(), nullable=False),
        sa.Column("current_status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "current_status IN ('active', 'inactive')",
            name="ck_drivers_valid_status",
        ),
        sa.PrimaryKeyConstraint("driver_id", name="pk_drivers"),
        sa.UniqueConstraint("email", name="uq_drivers_email"),
        sa.UniqueConstraint("phone", name="uq_drivers_phone"),
        sa.UniqueConstraint("license_number", name="uq_drivers_license_number"),
    )


def downgrade() -> None:
    op.drop_table("drivers")
