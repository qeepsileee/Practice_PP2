"""
Database layer for Snake TSIS 4.
Uses psycopg2 to connect to PostgreSQL.

Expected environment / config:
  DB_HOST  = localhost
  DB_PORT  = 5432
  DB_NAME  = snake_db
  DB_USER  = postgres
  DB_PASS  = (your password)

Create tables once with:
    python db.py --init
"""

import os
import sys
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# ── Connection settings ────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5432)),
    "dbname":   os.environ.get("DB_NAME",  "snake_db"),
    "user":     os.environ.get("DB_USER",  "postgres"),
    "password": os.environ.get("DB_PASS",  ""),
}

_conn = None   # module-level cached connection


def _get_conn():
    global _conn
    if not PSYCOPG2_AVAILABLE:
        return None
    try:
        if _conn is None or _conn.closed:
            _conn = psycopg2.connect(**DB_CONFIG)
        return _conn
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        return None


# ── Schema init ────────────────────────────────────────────────────────────────
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def init_db():
    conn = _get_conn()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_SQL)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        conn.rollback()
        return False


# ── Player helpers ─────────────────────────────────────────────────────────────

def get_or_create_player(username: str) -> int | None:
    """Return player id, creating the row if it doesn't exist."""
    conn = _get_conn()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id",
                (username,),
            )
            player_id = cur.fetchone()[0]
        conn.commit()
        return player_id
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        conn.rollback()
        return None


# ── Session helpers ────────────────────────────────────────────────────────────

def save_session(username: str, score: int, level_reached: int) -> bool:
    """Persist a finished game session."""
    conn = _get_conn()
    if conn is None:
        return False
    player_id = get_or_create_player(username)
    if player_id is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO game_sessions (player_id, score, level_reached)
                   VALUES (%s, %s, %s)""",
                (player_id, score, level_reached),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        conn.rollback()
        return False


def get_personal_best(username: str) -> int:
    """Return the player's all-time best score (0 if none)."""
    conn = _get_conn()
    if conn is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT MAX(gs.score)
                   FROM game_sessions gs
                   JOIN players p ON p.id = gs.player_id
                   WHERE p.username = %s""",
                (username,),
            )
            row = cur.fetchone()
        return row[0] if row and row[0] is not None else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top *limit* sessions as a list of dicts."""
    conn = _get_conn()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """SELECT p.username,
                          gs.score,
                          gs.level_reached,
                          gs.played_at
                   FROM game_sessions gs
                   JOIN players p ON p.id = gs.player_id
                   ORDER BY gs.score DESC
                   LIMIT %s""",
                (limit,),
            )
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []


# ── CLI helper ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--init" in sys.argv:
        ok = init_db()
        print("Tables created." if ok else "Failed (check DB_* env vars).")
