from langchain_core.tools import tool

from agent.audit.logger import log_action
from agent.sandbox.executor import execute


@tool
def code_exec(code: str) -> str:
    """Ejecuta código Python en sandbox seguro con timeout de 10 segundos."""
    log_action("code_tool", "exec", {"code_preview": code[:200]})

    result = execute(code)

    if result["error"]:
        log_action("code_tool", "exec_result", {"code_preview": code[:200]}, error=result["error"])
        return f"ERROR: {result['error']}"

    log_action("code_tool", "exec_result", {"code_preview": code[:200]}, result=result["output"])
    return result["output"] or "(sin output)"
