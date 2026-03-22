from pathlib import Path
from langchain_core.tools import tool
import yaml

from agent.audit.logger import log_action


def _load_config():
    with open("config/allowed_paths.yml") as f:
        return yaml.safe_load(f)


def _is_allowed(path: str, mode: str) -> bool:
    cfg = _load_config()
    resolved = Path(path).resolve()

    for denied in cfg.get("denied_patterns", []):
        if resolved.match(denied):
            return False

    allowed = cfg["allowed_paths"].get(mode, [])
    return any(str(resolved).startswith(str(Path(p).resolve())) for p in allowed)


@tool
def fs_read(path: str) -> str:
    """Lee el contenido de un archivo dentro de los paths permitidos."""
    if not _is_allowed(path, "read"):
        log_action("fs_tool", "read", {"path": path}, error="Path no permitido")
        return "ERROR: path no está en la allowlist de lectura."

    try:
        content = Path(path).read_text(encoding="utf-8")
        log_action("fs_tool", "read", {"path": path}, result=content)
        return content
    except Exception as e:
        log_action("fs_tool", "read", {"path": path}, error=str(e))
        return f"ERROR: {e}"


@tool
def fs_write(path: str, content: str) -> str:
    """Escribe contenido en un archivo dentro de los paths permitidos de escritura."""
    if not _is_allowed(path, "write"):
        log_action("fs_tool", "write", {"path": path}, error="Path no permitido")
        return "ERROR: path no está en la allowlist de escritura."

    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        log_action("fs_tool", "write", {"path": path, "bytes": len(content)}, result="ok")
        return f"Archivo escrito: {path}"
    except Exception as e:
        log_action("fs_tool", "write", {"path": path}, error=str(e))
        return f"ERROR: {e}"
