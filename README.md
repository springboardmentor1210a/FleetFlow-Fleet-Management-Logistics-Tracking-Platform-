# FleetFlow milestone implementation

Starter scaffold for the Week 1-2 implementation tasks in the FleetFlow brief.

## Current step

The project now includes React and FastAPI applications, PostgreSQL with Alembic migrations, JWT sign-in and role checks, vehicle registration and fleet search/status filtering, plus basic driver registration and listing. Shipment tracking, route optimization, maintenance, analytics and deployment are staged for later milestones.

## Prerequisites

- Python 3.10 or newer
- Node.js and npm
- Git

## Run the FastAPI backend

From `backend`:

```powershell
py -V:3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

These commands use the virtual environment directly, so PowerShell activation-policy settings do not need to change.

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is available at `/docs`; the health check is `/api/health`.

## Run the React frontend

In another terminal, from `frontend`:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite. The dashboard loads vehicle counts from PostgreSQL. Fleet Management provides vehicle search and status filtering; Driver Management provides driver registration and listing.

## Environment setup

Copy `backend/.env.example` to `backend/.env` and replace the placeholder password with the password you created for `fleetflow_app`. Keep `.env` private and do not commit it.

The API database check is available at `/api/health/database` after the backend starts.

## Apply database migrations

From `backend`, with `.env` configured and PostgreSQL running:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

This applies pending migrations, including the `vehicles`, `users` and `drivers` tables. The migration history is stored in `migrations/versions`.

## Create the first Administrator

Install updated backend dependencies, apply migrations, and then create the first account:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.create_admin
```

The account command prompts for a name, email and password. It stores only a password hash. The local `backend/.env` contains the JWT signing key; keep that file private. Sign in from the dashboard. Vehicle and driver registration require the Administrator or Fleet Manager role.

If you forget the Administrator password, run `.\.venv\Scripts\python.exe -m app.reset_admin_password` from `backend`. The command prompts for the Administrator email and a new password without echoing the password.

## Milestone sequence

1. Initialize frontend and backend applications. (This scaffold.)
2. Add PostgreSQL configuration, SQLAlchemy models and Alembic migrations.
3. Add authentication and role-based access for Administrator, Fleet Manager, Dispatcher and Driver.
4. Implement vehicle and driver registration, availability and fleet dashboard.
5. Implement trips, shipments, status history, GPS/map integration, route planning and ETA.
6. Add maintenance scheduling, driver assignment, alerts, analytics, exports, deployment and final documentation.

Use sample data and environment variables for local development. Connect external maps, GPS, email, SMS or cloud services only after their credentials and requirements are confirmed.

