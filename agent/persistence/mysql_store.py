import json
import os
import uuid
from datetime import datetime

import pymysql
import pymysql.cursors
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict


MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "dev_agent")


def _connect(database: str | None = MYSQL_DB):
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db() -> None:
    """Crea la base de datos y la tabla de sesiones si no existen."""
    con = _connect(database=None)
    with con.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    con.commit()
    con.close()

    con = _connect()
    with con.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          VARCHAR(36)  PRIMARY KEY,
                title       VARCHAR(255),
                messages    LONGTEXT     NOT NULL,
                created_at  DATETIME     NOT NULL,
                updated_at  DATETIME     NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    con.commit()
    con.close()


def new_thread_id() -> str:
    return str(uuid.uuid4())


def save_session(thread_id: str, messages: list[BaseMessage], title: str | None = None) -> None:
    payload = json.dumps(messages_to_dict(messages), ensure_ascii=False)
    now = datetime.utcnow()
    con = _connect()
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO sessions (id, title, messages, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                messages   = VALUES(messages),
                updated_at = VALUES(updated_at),
                title      = COALESCE(VALUES(title), title)
        """, (thread_id, title, payload, now, now))
    con.commit()
    con.close()


def load_session(thread_id: str) -> list[BaseMessage]:
    con = _connect()
    with con.cursor() as cur:
        cur.execute("SELECT messages FROM sessions WHERE id = %s", (thread_id,))
        row = cur.fetchone()
    con.close()
    if not row:
        return []
    return messages_from_dict(json.loads(row["messages"]))


def list_sessions(limit: int = 20) -> list[dict]:
    con = _connect()
    with con.cursor() as cur:
        cur.execute(
            "SELECT id, title, created_at, updated_at FROM sessions "
            "ORDER BY updated_at DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    con.close()
    return rows
