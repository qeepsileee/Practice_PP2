import psycopg2
from config import config


def connect():
    """Return a psycopg2 connection or None on failure."""
    try:
        conn = psycopg2.connect(**config)
        return conn
    except psycopg2.OperationalError as e:
        print(f"[DB] Connection error: {e}")
        return None
