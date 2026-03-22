# Tools

Cada tool es una función decorada con `@tool` de LangChain. El registro activo se controla desde `config/tools_manifest.yml`.

## fs_tool — Sistema de archivos

**Funciones:** `fs_read(path)`, `fs_write(path, content)`

**Config:** `config/allowed_paths.yml`

```yaml
allowed_paths:
  read:  [./examples, ./wiki, /tmp/agent-workspace]
  write: [/tmp/agent-workspace]
```

Para agregar un path permitido, edita el YAML — no el código.

---

## web_tool — Web

**Función:** `web_search(url)`

**Config:** `config/allowed_domains.yml`

Solo GET. Respuesta truncada a 3000 caracteres. Para agregar un dominio edita la allowlist.

---

## code_tool — Ejecución de código

**Función:** `code_exec(code)`

Pasa por `sandbox/executor.py` → `RestrictedPython`.

**Lo que NO puede hacer el código:**
- `import os`, `import subprocess`, `import sys`
- `open()` directo al filesystem
- Loops infinitos (timeout 10s)
- Acceso a `__builtins__` completo

---

## db_tool — Base de datos

**Función:** `db_query(query)`

- Solo acepta queries que empiecen con `SELECT`
- Conexión SQLite en modo read-only
- Máximo 50 filas en resultado
- Path configurable via `AGENT_DB_PATH`

---

## Agregar una nueva tool

1. Crear `agent/tools/mi_tool.py` con `@tool`
2. Importarla en `agent/tools/__init__.py` → `_ALL_TOOLS`
3. Declarar en `config/tools_manifest.yml`
4. Documentar en esta wiki
