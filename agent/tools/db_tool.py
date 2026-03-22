import os
import re
import sqlite3
from langchain_core.tools import tool

from agent.audit.logger import log_action


READONLY_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
DB_PATH = os.getenv("AGENT_DB_PATH", "/tmp/agent-workspace/agent.db")


def _is_readonly(query: str) -> bool:
    return bool(READONLY_PATTERN.match(query.strip()))


@tool
def db_query(query: str) -> str:
    """Ejecuta una query SELECT de solo lectura contra la base de datos del agente."""
    if not _is_readonly(query):
        log_action("db_tool", "query", {"query": query}, error="Solo se permiten SELECT")
        return "ERROR: solo se permiten queries SELECT."

    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        con.close()

        result = {"columns": columns, "rows": rows[:50]}
        log_action("db_tool", "query", {"query": query}, result=str(result))
        return str(result)
    except Exception as e:
        log_action("db_tool", "query", {"query": query}, error=str(e))
        return f"ERROR: {e}"
