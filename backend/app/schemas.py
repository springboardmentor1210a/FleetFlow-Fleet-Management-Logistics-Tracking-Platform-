"""Request and response schemas for FleetFlow API resources."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


VehicleStatus = Literal["available", "assigned", "maintenance", "inactive"]
UserRole = Literal["administrator", "fleet_manager", "dispatcher", "driver"]
DriverStatus = Literal["active", "inactive"]


class VehicleCreate(BaseModel):
    registration_no: str = Field(min_length=1, max_length=20)
    vehicle_type: str = Field(min_length=1, max_length=50)
    capacity_kg: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    fuel_type: str = Field(min_length=1, max_length=30)
    current_status: VehicleStatus = "available"

    @field_validator("registration_no", "vehicle_type", "fuel_type")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: int
    registration_no: str
    vehicle_type: str
    capacity_kg: Decimal
    fuel_type: str
    current_status: VehicleStatus
    created_at: datetime


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


class DriverCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    phone: str = Field(min_length=7, max_length=20)
    license_number: str = Field(min_length=1, max_length=40)
    license_expiry: date
    current_status: DriverStatus = "active"

    @field_validator("full_name", "license_number")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_optional_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        email = value.strip().lower()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address")
        return email

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        phone = value.strip()
        if not any(character.isdigit() for character in phone):
            raise ValueError("Enter a valid phone number")
        return phone


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: int
    full_name: str
    email: str | None
    phone: str
    license_number: str
    license_expiry: date
    current_status: DriverStatus
    created_at: datetime
