# Configuración

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servidor Ollama |
| `OLLAMA_MODEL` | `llama3.1:8b` | Modelo a usar (debe soportar tool calling) |
| `MYSQL_HOST` | `localhost` | Host de MySQL |
| `MYSQL_PORT` | `3306` | Puerto de MySQL |
| `MYSQL_USER` | `root` | Usuario de MySQL |
| `MYSQL_PASSWORD` | `` (vacío) | Contraseña de MySQL |
| `MYSQL_DB` | `dev_agent` | Base de datos (se crea automáticamente) |

### Configurar en Windows

```cmd
set OLLAMA_MODEL=llama3.1:8b
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=mipassword
set MYSQL_DB=dev_agent
```

### Configurar en Linux / Mac

```bash
export OLLAMA_MODEL=llama3.1:8b
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=mipassword
export MYSQL_DB=dev_agent
```

### Usando archivo `.env`

Copia `.env.example` a `.env` y edita los valores:

```bash
cp .env.example .env
```

> `.env` está en `.gitignore` — nunca se sube al repositorio.

---

## Modelos compatibles con tool calling

Solo modelos que soporten tool calling estructurado funcionan correctamente como orquestador:

| Modelo | Tool calling | Tamaño | Notas |
|---|---|---|---|
| `llama3.1:8b` | ✅ Nativo | 8B / ~4.7GB | **Recomendado** |
| `llama3.1:70b` | ✅ Nativo | 70B / ~40GB | Requiere hardware potente |
| `qwen2.5:7b` | ✅ | 7B / ~4.5GB | Alternativa válida |
| `mistral-nemo` | ✅ | 12B | Buena alternativa |
| `qwen2.5-coder:latest` | ⚠️ Parcial | 7.6B | No genera tool_calls estructurados vía Ollama |
| `phi3` | ❌ | 3.8B | Sin tool calling |
| `codellama` | ❌ | 7B | Sin tool calling |

---

## Archivos de configuración YAML

### `config/allowed_paths.yml`

Controla qué rutas puede leer/escribir `fs_tool`:

```yaml
allowed_paths:
  read:
    - .                        # directorio raíz del proyecto
    - ./examples
    - ./wiki
    - /tmp/agent-workspace
  write:
    - /tmp/agent-workspace     # única ruta de escritura

denied_patterns:               # bloqueados aunque estén en read
  - "*.env"
  - "*.pem"
  - "*.key"
  - "*secret*"
  - "*credential*"
```

### `config/allowed_domains.yml`

Controla a qué URLs puede hacer GET `web_tool`:

```yaml
allowed_domains:
  - docs.python.org
  - pypi.org
  - stackoverflow.com
  - github.com
  - developer.mozilla.org
  - docs.anthropic.com
  - docs.langchain.com

blocked_methods:
  - POST
  - PUT
  - DELETE
  - PATCH
```

### `config/tools_manifest.yml`

Activa o desactiva tools sin modificar código:

```yaml
tools:
  fs_tool:
    enabled: true
    risk_level: medium

  web_tool:
    enabled: true
    risk_level: low

  code_tool:
    enabled: true
    risk_level: high
    sandbox: true
    timeout_seconds: 10

  db_tool:
    enabled: true
    risk_level: medium
    readonly: true
```

---

## System prompt del agente

El system prompt en `agent/graph.py` guía al LLM en la selección de tools. Se inyecta automáticamente en el primer turno de cada conversación y **no** se persiste en MySQL (se regenera en cada arranque).

Para modificar el comportamiento del agente, edita la constante `SYSTEM_PROMPT` en [agent/graph.py](../agent/graph.py).
