
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

DB_PATH = Path(
    os.getenv("DB_PATH", str(BASE_DIR / "data" / "parcel.db"))
)

# Match the ESP32 zero threshold
EMPTY_THRESHOLD_G = 0.5

app = FastAPI(title="PARCELGUARD - Smart Parcel Verification")

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")

    return db


def initialize_database():

    with get_connection() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK(id=1),
                expected_weight_g REAL NOT NULL DEFAULT 400,
                tolerance_g REAL NOT NULL DEFAULT 5
            )
        """)

        db.execute("""
            INSERT OR IGNORE INTO settings
            (id, expected_weight_g, tolerance_g)
            VALUES (1, 400, 5)
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actual_weight_g REAL NOT NULL,
                expected_weight_g REAL NOT NULL,
                tolerance_g REAL NOT NULL,
                status TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(readings)"
            ).fetchall()
        }

        # Migrate the older database format if necessary
        if "actual_weight_g" not in columns and "actual_weight" in columns:

            print("Migrating old database...")

            db.execute("""
                CREATE TABLE readings_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actual_weight_g REAL NOT NULL,
                    expected_weight_g REAL NOT NULL,
                    tolerance_g REAL NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            db.execute("""
                INSERT INTO readings_new
                SELECT
                    id,
                    actual_weight,
                    expected_weight,
                    5,
                    status,
                    source,
                    created_at
                FROM readings
            """)

            db.execute("DROP TABLE readings")

            db.execute("""
                ALTER TABLE readings_new
                RENAME TO readings
            """)

            print("Database migration completed.")

        required = {
            "id",
            "actual_weight_g",
            "expected_weight_g",
            "tolerance_g",
            "status",
            "source",
            "created_at"
        }

        final_columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(readings)"
            ).fetchall()
        }

        if not required.issubset(final_columns):
            raise RuntimeError("Unsupported readings database structure.")

    print("Database initialized successfully.")


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

    with get_connection() as db:
        row = db.execute("""
            SELECT expected_weight_g, tolerance_g
            FROM settings
            WHERE id=1
        """).fetchone()

    return dict(row)


@app.get("/api/settings")
def read_settings():
    return get_settings()


@app.put("/api/settings")
def update_settings(settings: VerificationSettings):

    with get_connection() as db:
        db.execute("""
            UPDATE settings
            SET expected_weight_g=?,
                tolerance_g=?
            WHERE id=1
        """, (
            settings.expected_weight_g,
            settings.tolerance_g
        ))

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
        "project": "PARCELGUARD"
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

    with get_connection() as db:

        cursor = db.execute("""
            INSERT INTO readings (
                actual_weight_g,
                expected_weight_g,
                tolerance_g,
                status,
                source,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            actual,
            expected,
            tolerance,
            status,
            reading.source,
            created_at
        ))

        reading_id = cursor.lastrowid

    print(
        f"Reading: {actual} g | "
        f"Expected: {expected} g | "
        f"Tolerance: {tolerance} g | "
        f"Status: {status}"
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

    with get_connection() as db:

        latest = db.execute("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        history = db.execute("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        total = db.execute("""
            SELECT COUNT(*) AS n
            FROM readings
        """).fetchone()["n"]

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

    with get_connection() as db:
        rows = db.execute("""
            SELECT *
            FROM readings
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


print("PARCELGUARD backend loaded.")
print(f"Database location: {DB_PATH}")
