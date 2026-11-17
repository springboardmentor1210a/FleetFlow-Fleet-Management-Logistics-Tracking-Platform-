import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .auth import create_access_token, password_hasher, require_roles
from .database import engine, get_db
from .models import Driver, User, Vehicle
from .schemas import (
    DriverCreate,
    DriverRead,
    LoginRequest,
    TokenResponse,
    UserRead,
    VehicleCreate,
    VehicleRead,
)

app = FastAPI(
    title="FleetFlow API",
    description="Fleet management and logistics operations API.",
    version="0.1.0",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/api/health", tags=["system"])
def health_check():
    """Report that the API process is responding."""
    return {"status": "ok", "service": "fleetflow-api"}


@app.get("/api/health/database", tags=["system"])
def database_health_check():
    """Check that the API can open a connection to PostgreSQL."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503, detail="Database connection failed"
        ) from exc
    return {"status": "ok", "database": "connected"}


@app.post("/api/auth/login", response_model=TokenResponse, tags=["authentication"])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an active user and issue a short-lived access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not user.is_active or not password_hasher.verify(
        payload.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user))


@app.get("/api/auth/me", response_model=UserRead, tags=["authentication"])
def current_user(user: User = Depends(require_roles(
    "administrator", "fleet_manager", "dispatcher", "driver"
))):
    """Return the signed-in user's public profile and role."""
    return user


@app.get("/api/vehicles", response_model=list[VehicleRead], tags=["vehicles"])
def list_vehicles(db: Session = Depends(get_db)):
    """Return registered vehicles, newest first."""
    return db.scalars(select(Vehicle).order_by(Vehicle.created_at.desc())).all()


@app.post(
    "/api/vehicles",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["vehicles"],
)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("administrator", "fleet_manager")),
):
    """Register a vehicle in the fleet."""
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A vehicle with this registration number already exists.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the vehicle. Check the database connection.",
        ) from exc
    db.refresh(vehicle)
    return vehicle


@app.get("/api/drivers", response_model=list[DriverRead], tags=["drivers"])
def list_drivers(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "administrator", "fleet_manager", "dispatcher", "driver"
    )),
):
    """List driver profiles for authenticated FleetFlow users."""
    return db.scalars(select(Driver).order_by(Driver.created_at.desc())).all()


@app.post(
    "/api/drivers",
    response_model=DriverRead,
    status_code=status.HTTP_201_CREATED,
    tags=["drivers"],
)
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("administrator", "fleet_manager")),
):
    """Register a driver profile for future trip assignment."""
    driver = Driver(**payload.model_dump())
    db.add(driver)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A driver with this email, phone number, or license number already exists.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the driver. Check the database connection.",
        ) from exc
    db.refresh(driver)
    return driver
