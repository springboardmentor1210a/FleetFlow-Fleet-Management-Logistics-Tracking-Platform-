"""Initial FleetFlow database models."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Vehicle(Base):
    """A vehicle registered in the FleetFlow fleet."""

    __tablename__ = "vehicles"
    __table_args__ = (
        CheckConstraint("capacity_kg > 0", name="positive_capacity"),
        CheckConstraint(
            "current_status IN ('available', 'assigned', 'maintenance', 'inactive')",
            name="valid_status",
        ),
    )

    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    registration_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fuel_type: Mapped[str] = mapped_column(String(30), nullable=False)
    current_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="available", server_default="available"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class User(Base):
    """A FleetFlow user account with an assigned operational role."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('administrator', 'fleet_manager', 'dispatcher', 'driver')",
            name="valid_role",
        ),
    )

    user_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Driver(Base):
    """A driver profile available for future trip assignment."""

    __tablename__ = "drivers"
    __table_args__ = (
        CheckConstraint(
            "current_status IN ('active', 'inactive')",
            name="valid_status",
        ),
    )

    driver_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    license_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    license_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    current_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
