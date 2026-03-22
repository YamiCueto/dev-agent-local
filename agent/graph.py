import os
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import get_active_tools
from agent.audit.logger import log_action


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

tools = get_active_tools()
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
).bind_tools(tools)


def planner(state: AgentState) -> AgentState:
    """LLM decide qué tool usar o genera respuesta final."""
    response = llm.invoke(state["messages"])
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
