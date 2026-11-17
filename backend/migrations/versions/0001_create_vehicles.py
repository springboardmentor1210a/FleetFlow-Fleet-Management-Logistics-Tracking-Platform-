"""Create the initial vehicles table."""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_vehicles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("registration_no", sa.String(length=20), nullable=False),
        sa.Column("vehicle_type", sa.String(length=50), nullable=False),
        sa.Column("capacity_kg", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("fuel_type", sa.String(length=30), nullable=False),
        sa.Column(
            "current_status",
            sa.String(length=20),
            server_default="available",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("capacity_kg > 0", name="ck_vehicles_positive_capacity"),
        sa.CheckConstraint(
            "current_status IN ('available', 'assigned', 'maintenance', 'inactive')",
            name="ck_vehicles_valid_status",
        ),
        sa.PrimaryKeyConstraint("vehicle_id", name="pk_vehicles"),
        sa.UniqueConstraint("registration_no", name="uq_vehicles_registration_no"),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
