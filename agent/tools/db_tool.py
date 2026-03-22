import os
import re

import pymysql
import pymysql.cursors
from langchain_core.tools import tool

from agent.audit.logger import log_action


READONLY_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)


def _connect():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DB", "dev_agent"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


@tool
def db_query(query: str) -> str:
    """Ejecuta una query SELECT de solo lectura contra la base de datos MySQL del agente."""
    if not READONLY_PATTERN.match(query.strip()):
        log_action("db_tool", "query", {"query": query}, error="Solo se permiten SELECT")
        return "ERROR: solo se permiten queries SELECT."

    try:
        con = _connect()
        with con.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchmany(50)
        con.close()
        result = str(rows)
        log_action("db_tool", "query", {"query": query}, result=result)
        return result
    except Exception as e:
        log_action("db_tool", "query", {"query": query}, error=str(e))
        return f"ERROR: {e}"
