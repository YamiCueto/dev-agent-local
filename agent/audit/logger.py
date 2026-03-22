import json
import logging
from datetime import datetime, timezone
from pathlib import Path


LOG_DIR = Path("/tmp/agent-audit")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "audit.jsonl"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("audit")


def log_action(
    tool: str,
    action: str,
    input_data: dict,
    result: str | None = None,
    error: str | None = None,
) -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "action": action,
        "input": input_data,
        "result_preview": result[:200] if result else None,
        "error": error,
        "status": "error" if error else "ok",
    }
    logger.info(json.dumps(entry))
    return entry
