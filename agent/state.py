from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tool_calls: List[dict]
    current_tool: Optional[str]
    tool_result: Optional[str]
    audit_log: List[dict]
    iteration: int
    error: Optional[str]
