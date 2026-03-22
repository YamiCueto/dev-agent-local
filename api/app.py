import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent.main import run as agent_run
from agent.persistence.mysql_store import (
    init_db,
    new_thread_id,
    save_session,
    load_session,
    list_sessions,
    _connect,
)


class UnicodeJSONResponse(JSONResponse):
    """JSONResponse con ensure_ascii=False para tildes y ñ correctas."""
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False).encode("utf-8")


app = FastAPI(title="Dev Agent Local API", default_response_class=UnicodeJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


# ── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.get("/api/sessions")
async def get_sessions():
    sessions = list_sessions()
    return [
        {
            "id": s["id"],
            "title": s["title"] or "(sin título)",
            "updated_at": s["updated_at"].isoformat() if s["updated_at"] else None,
        }
        for s in sessions
    ]


@app.get("/api/sessions/{thread_id}")
async def get_session(thread_id: str):
    messages = load_session(thread_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return [
        {"role": type(m).__name__.replace("Message", "").lower(), "content": m.content}
        for m in messages
        if hasattr(m, "content") and m.content
    ]


@app.delete("/api/sessions/{thread_id}")
async def delete_session(thread_id: str):
    con = _connect()
    with con.cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE id = %s", (thread_id,))
    con.commit()
    con.close()
    return {"ok": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    thread_id = req.thread_id or new_thread_id()
    history = load_session(thread_id) if req.thread_id else []

    response, new_history = await asyncio.to_thread(agent_run, req.message, history)

    title = req.message[:80] if not history else None
    save_session(thread_id, new_history, title=title)

    return {"response": response, "thread_id": thread_id}
