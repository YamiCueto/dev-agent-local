from urllib.parse import urlparse
import httpx
import yaml
from langchain_core.tools import tool

from agent.audit.logger import log_action


def _load_config():
    with open("config/allowed_domains.yml") as f:
        return yaml.safe_load(f)


def _is_allowed_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lstrip("www.")
    allowed = _load_config()["allowed_domains"]
    return any(domain == d or domain.endswith(f".{d}") for d in allowed)


@tool
def web_search(url: str) -> str:
    """Hace una petición GET a una URL dentro de los dominios permitidos."""
    if not _is_allowed_domain(url):
        log_action("web_tool", "get", {"url": url}, error="Dominio no permitido")
        return "ERROR: dominio no está en la allowlist."

    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        text = resp.text[:3000]
        log_action("web_tool", "get", {"url": url, "status": resp.status_code}, result=text)
        return text
    except Exception as e:
        log_action("web_tool", "get", {"url": url}, error=str(e))
        return f"ERROR: {e}"
