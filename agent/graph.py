import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import get_active_tools
from agent.audit.logger import log_action


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

SYSTEM_PROMPT = """Eres un asistente de desarrollo local. Tienes acceso a estas tools:

- fs_read(path): lee archivos del filesystem. Úsala SOLO cuando el usuario pida explícitamente leer o ver un archivo.
- fs_write(path, content): escribe archivos. Úsala SOLO cuando el usuario pida explícitamente guardar, crear o escribir un archivo.
- web_search(url): hace GET a una URL permitida. Úsala para consultar documentación online.
- code_exec(code): ejecuta código Python en sandbox. Úsala para cálculos, scripts o demos.
- db_query(query): ejecuta SELECT en la base de datos local.

Reglas CRÍTICAS (debes seguirlas siempre):
1. NUNCA uses fs_write a menos que el usuario diga EXPLÍCITAMENTE "guarda", "escribe", "crea el archivo", "modifica el archivo" u orden similar. Para preguntas conversacionales, responde directamente sin ninguna tool.
2. NUNCA uses fs_read a menos que el usuario pida EXPLÍCITAMENTE ver o leer un archivo. No leas archivos para responder preguntas generales.
3. Para preguntas como "cómo funciona X", "qué es Y", "cómo te actualizo" — responde directamente con tu conocimiento, SIN usar ninguna tool.
4. Para leer archivos usa paths relativos como "./archivo.py". Nunca uses paths absolutos.
5. Para buscar en la web usa web_search, nunca code_exec con urllib.
6. Usa code_exec solo para ejecutar lógica Python que no requiera acceso a red ni filesystem.
7. Si una tool falla, informa el error al usuario sin inventar el resultado.
8. SIEMPRE responde en texto plano o markdown. NUNCA respondas con JSON, XML ni ningún formato estructurado de datos.
9. Responde directamente al usuario de forma natural y conversacional. Nunca uses frases técnicas como "status: operational"."""

tools = get_active_tools()
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
).bind_tools(tools)


def planner(state: AgentState) -> AgentState:
    """LLM decide qué tool usar o genera respuesta final."""
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    response = llm.invoke(messages)
    return {
        "messages": [response],
        "iteration": state.get("iteration", 0) + 1,
    }


def auditor(state: AgentState) -> AgentState:
    """Registra la última acción del tool antes de continuar."""
    messages = state.get("messages", [])
    last = messages[-1] if messages else None

    if last and hasattr(last, "name"):
        entry = log_action(
            tool=last.name,
            action="tool_response",
            input_data={},
            result=str(last.content)[:300] if last.content else None,
        )
        return {"audit_log": state.get("audit_log", []) + [entry]}

    return {}


def should_continue(state: AgentState) -> str:
    """Decide si hay más tool_calls o terminamos."""
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def build_graph() -> StateGraph:
    tool_node = ToolNode(tools)

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("tools", tool_node)
    graph.add_node("auditor", auditor)

    graph.set_entry_point("planner")
    graph.add_conditional_edges("planner", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "auditor")
    graph.add_edge("auditor", "planner")

    return graph.compile()
