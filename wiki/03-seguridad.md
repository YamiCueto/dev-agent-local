# Seguridad

Ver [SECURITY.md](../SECURITY.md) para el resumen ejecutivo.

## Capas de defensa

```
Request del LLM
      ↓
1. tools_manifest.yml   ← ¿tool habilitada?
      ↓
2. Validación en tool   ← allowlist path / dominio / regex SELECT
      ↓
3. Sandbox / modo RO    ← RestrictedPython o SQLite ro URI
      ↓
4. Audit log            ← entrada registrada ANTES de retornar resultado
      ↓
Resultado al LLM
```

## Qué auditar

Cada entrada en `audit/logger.py` incluye:
- `timestamp` UTC
- `tool` y `action`
- `input` (datos enviados a la tool)
- `result_preview` (primeros 200 chars del resultado)
- `error` si falló
- `status`: `ok` | `error`

Los logs van a `/tmp/agent-audit/audit.jsonl` en formato JSONL (una entrada por línea).

## Extender la sandbox

`RestrictedPython` permite listas de imports seguros. Para permitir `math` o `json` en la sandbox:

```python
from RestrictedPython import safe_globals
restricted_globals["__builtins__"]["__import__"] = safe_import_factory(["math", "json"])
```

Editar `agent/sandbox/executor.py`.
