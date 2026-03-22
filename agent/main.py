import sys

from langchain_core.messages import HumanMessage

from agent.graph import build_graph
from agent.persistence.mysql_store import (
    init_db,
    new_thread_id,
    save_session,
    load_session,
    list_sessions,
)

# Forzar UTF-8 en consola Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

GRAPH = None


def get_graph():
    global GRAPH
    if GRAPH is None:
        GRAPH = build_graph()
    return GRAPH


def run(user_input: str, history: list) -> tuple[str, list]:
    """Ejecuta un turno del agente. Retorna (respuesta, historial actualizado)."""
    graph = get_graph()
    messages = history + [HumanMessage(content=user_input)]
    result = graph.invoke({
        "messages": messages,
        "tool_calls": [],
        "current_tool": None,
        "tool_result": None,
        "audit_log": [],
        "iteration": 0,
        "error": None,
    })
    updated_messages = result["messages"]
    response = updated_messages[-1].content
    return response, list(updated_messages)


def pick_session() -> tuple[str, list]:
    """Muestra sesiones anteriores y deja al usuario elegir o crear una nueva."""
    sessions = list_sessions()

    if sessions:
        print("\nSesiones anteriores:")
        for i, s in enumerate(sessions, 1):
            title = s["title"] or "(sin título)"
            updated = s["updated_at"].strftime("%Y-%m-%d %H:%M") if s["updated_at"] else ""
            print(f"  [{i}] {title}  —  {updated}")
        print("  [n] Nueva sesión")
        print()

        choice = input("Elige sesión >>> ").strip().lower()
        if choice != "n" and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                sid = sessions[idx]["id"]
                history = load_session(sid)
                print(f"\nSesión cargada ({len(history)} mensajes previos)\n")
                return sid, history

    thread_id = new_thread_id()
    print(f"\nNueva sesión: {thread_id[:8]}...\n")
    return thread_id, []


def main():
    init_db()
    print("Dev Agent Local — escribe 'salir' para terminar, 'nueva' para cambiar sesión\n")

    thread_id, history = pick_session()
    title_set = len(history) > 0  # si cargamos sesión ya tiene título

    while True:
        try:
            user = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if user.lower() in {"salir", "exit", "quit"}:
            break

        if user.lower() == "nueva":
            thread_id, history = pick_session()
            title_set = len(history) > 0
            continue

        if not user:
            continue

        response, history = run(user, history)
        print(f"\n{response}\n")

        # Usa el primer mensaje del usuario como título de la sesión
        title = user[:80] if not title_set else None
        save_session(thread_id, history, title=title)
        title_set = True


if __name__ == "__main__":
    main()
