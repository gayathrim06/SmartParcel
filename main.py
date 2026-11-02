
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from sqlalchemy import create_engine, text, inspect

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

DATABASE_URL = os.getenv("DATABASE_URL")

# Render PostgreSQL URLs may begin with postgres://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

# Use PostgreSQL on Render and SQLite locally
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )
    DATABASE_TYPE = "PostgreSQL"
else:
    DB_PATH = BASE_DIR / "data" / "parcel.db"
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        f"sqlite:///{DB_PATH.as_posix()}",
        connect_args={"check_same_thread": False}
    )
    DATABASE_TYPE = "SQLite"

EMPTY_THRESHOLD_G = 0.5

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PARCELGUARD - Smart Parcel Verification")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def initialize_database():

    with engine.begin() as db:

        if DATABASE_TYPE == "PostgreSQL":

            db.execute(text("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    expected_weight_g DOUBLE PRECISION NOT NULL DEFAULT 400,
                    tolerance_g DOUBLE PRECISION NOT NULL DEFAULT 5
                )
            """))

            db.execute(text("""
                CREATE TABLE IF NOT EXISTS readings (
                    id BIGSERIAL PRIMARY KEY,
                    actual_weight_g DOUBLE PRECISION NOT NULL,
                    expected_weight_g DOUBLE PRECISION NOT NULL,
                    tolerance_g DOUBLE PRECISION NOT NULL,
                    status VARCHAR(30) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    created_at TEXT NOT NULL
                )
            """))

        else:

            db.execute(text("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    expected_weight_g REAL NOT NULL DEFAULT 400,
                    tolerance_g REAL NOT NULL DEFAULT 5
                )
            """))

            db.execute(text("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actual_weight_g REAL NOT NULL,
                    expected_weight_g REAL NOT NULL,
                    tolerance_g REAL NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """))

        # Insert default settings only if they do not exist
        if DATABASE_TYPE == "PostgreSQL":
            db.execute(text("""
                INSERT INTO settings
                (id, expected_weight_g, tolerance_g)
                VALUES (1, 400, 5)
                ON CONFLICT (id) DO NOTHING
            """))
        else:
            db.execute(text("""
                INSERT OR IGNORE INTO settings
                (id, expected_weight_g, tolerance_g)
                VALUES (1, 400, 5)
            """))

        # Check and migrate older SQLite readings table
        if DATABASE_TYPE == "SQLite":

            columns = {
                column["name"]
                for column in inspect(engine).get_columns("readings")
            }

            if "actual_weight_g" not in columns and "actual_weight" in columns:

                print("Migrating older SQLite readings table...")

                db.execute(text("""
                    ALTER TABLE readings
                    ADD COLUMN actual_weight_g REAL
                """))

                db.execute(text("""
                    UPDATE readings
                    SET actual_weight_g = actual_weight
                """))

                if "tolerance_g" not in columns:
                    db.execute(text("""
                        ALTER TABLE readings
                        ADD COLUMN tolerance_g REAL NOT NULL DEFAULT 5
                    """))

                print("Older SQLite migration completed.")

    print(f"{DATABASE_TYPE} database initialized successfully.")


initialize_database()

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class SensorReading(BaseModel):
    actual_weight_g: float = Field(ge=0, le=100000)
    source: str = "ESP32"


class VerificationSettings(BaseModel):
    expected_weight_g: float = Field(gt=0, le=100000)
    tolerance_g: float = Field(ge=0, le=10000)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

def get_settings():

    with engine.connect() as db:
        row = db.execute(text("""
            SELECT expected_weight_g, tolerance_g
            FROM settings
            WHERE id = 1
        """)).mappings().first()

    if row is None:
        raise RuntimeError("Settings record not found.")

    return dict(row)


@app.get("/api/settings")
def read_settings():
    return get_settings()


@app.put("/api/settings")
def update_settings(settings: VerificationSettings):

    with engine.begin() as db:
        db.execute(text("""
            UPDATE settings
            SET expected_weight_g = :expected,
                tolerance_g = :tolerance
            WHERE id = 1
        """), {
            "expected": settings.expected_weight_g,
            "tolerance": settings.tolerance_g
        })

    return {
        "message": "Settings saved successfully",
        **get_settings()
    }


# --------------------------------------------------
# STATUS VERIFICATION
# --------------------------------------------------

def get_status(actual, expected, tolerance):

    if actual <= EMPTY_THRESHOLD_G:
        return "NO PARCEL"

    minimum = expected - tolerance
    maximum = expected + tolerance

    if actual < minimum:
        return "UNDERWEIGHT"

    if actual > maximum:
        return "OVERWEIGHT"

    return "MATCH"


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "project": "PARCELGUARD",
        "database": DATABASE_TYPE
    }


# --------------------------------------------------
# RECEIVE ESP32 SENSOR DATA
# --------------------------------------------------

@app.post("/api/sensor")
def receive_sensor_reading(reading: SensorReading):

    settings = get_settings()

    actual = round(reading.actual_weight_g, 2)
    expected = float(settings["expected_weight_g"])
    tolerance = float(settings["tolerance_g"])

    status = get_status(
        actual,
        expected,
        tolerance
    )

    created_at = datetime.now(timezone.utc).isoformat()

    with engine.begin() as db:

        result = db.execute(text("""
            INSERT INTO readings (
                actual_weight_g,
                expected_weight_g,
                tolerance_g,
                status,
                source,
                created_at
            )
            VALUES (
                :actual,
                :expected,
                :tolerance,
                :status,
                :source,
                :created_at
            )
            RETURNING id
        """), {
            "actual": actual,
            "expected": expected,
            "tolerance": tolerance,
            "status": status,
            "source": reading.source,
            "created_at": created_at
        })

        reading_id = result.scalar_one()

    print(
        f"Reading: {actual} g | "
        f"Expected: {expected} g | "
        f"Tolerance: {tolerance} g | "
        f"Status: {status} | "
        f"Database: {DATABASE_TYPE}"
    )

    return {
        "id": reading_id,
        "actual_weight_g": actual,
        "expected_weight_g": expected,
        "tolerance_g": tolerance,
        "status": status,
        "source": reading.source,
        "created_at": created_at
    }


# --------------------------------------------------
# DASHBOARD DATA
# --------------------------------------------------

@app.get("/api/dashboard")
def dashboard_data(limit: int = 120):

    limit = max(1, min(limit, 500))

    settings = get_settings()

    with engine.connect() as db:

        latest = db.execute(text("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT 1
        """)).mappings().first()

        history = db.execute(text("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

        total = db.execute(text("""
            SELECT COUNT(*) AS n
            FROM readings
        """)).scalar_one()

    return {
        "settings": settings,
        "latest": dict(latest) if latest else None,
        "history": [
            dict(row) for row in reversed(history)
        ],
        "total_readings": total
    }


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

@app.get("/api/history")
def reading_history(limit: int = 50):

    limit = max(1, min(limit, 500))

    with engine.connect() as db:
        rows = db.execute(text("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT :limit
        """), {
            "limit": limit
        }).mappings().all()

    return [dict(row) for row in rows]


print("PARCELGUARD backend loaded.")
print(f"Active database: {DATABASE_TYPE}")
