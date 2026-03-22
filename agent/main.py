import os
import sys
from langchain_core.messages import HumanMessage
from agent.graph import build_graph

# Forzar UTF-8 en consola Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")


def run(user_input: str) -> str:
    graph = build_graph()
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "tool_calls": [],
            "current_tool": None,
            "tool_result": None,
            "audit_log": [],
            "iteration": 0,
            "error": None,
        }
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    print("Dev Agent Local — escribe 'salir' para terminar\n")
    while True:
        try:
            user = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user.lower() in {"salir", "exit", "quit"}:
            break
        if not user:
            continue
        response = run(user)
        print(f"\n{response}\n")
