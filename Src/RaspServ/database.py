"""SQLite storage for sensor history, with timestamps in UTC."""

from contextlib import closing
from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).resolve().with_name("measurements.db")


def initialize_database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL,
                    humidity REAL,
                    light REAL
                )
            """)
            connection.execute("""
                CREATE INDEX IF NOT EXISTS measurements_timestamp
                ON measurements (timestamp)
            """)


def save_measurement(status):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO measurements (temperature, humidity, light) "
                "VALUES (?, ?, ?)",
                (status.get("temperature"), status.get("humidity"),
                 status.get("light")),
            )


def _query(sql, parameters=()):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql, parameters)]


def get_measurements():
    return _query(
        "SELECT timestamp, temperature, humidity, light "
        "FROM measurements ORDER BY timestamp, id"
    )


def get_measurements_since(minutes):
    return _query(
        "SELECT timestamp, temperature, humidity, light FROM measurements "
        "WHERE timestamp >= datetime('now', ?) ORDER BY timestamp, id",
        (f"-{int(minutes)} minutes",),
    )
