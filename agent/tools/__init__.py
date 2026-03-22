import yaml
from agent.tools.fs_tool import fs_read, fs_write
from agent.tools.web_tool import web_search
from agent.tools.code_tool import code_exec
from agent.tools.db_tool import db_query

_ALL_TOOLS = {
    "fs_tool": [fs_read, fs_write],
    "web_tool": [web_search],
    "code_tool": [code_exec],
    "db_tool": [db_query],
}


def get_active_tools() -> list:
    """Retorna solo las tools habilitadas en tools_manifest.yml."""
    with open("config/tools_manifest.yml") as f:
        manifest = yaml.safe_load(f)

    active = []
    for name, cfg in manifest["tools"].items():
        if cfg.get("enabled"):
            active.extend(_ALL_TOOLS.get(name, []))
    return active
