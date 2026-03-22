# Dev Agent Local

Agente de desarrollo local orquestado con **LangGraph** + **Claude**, con 4 tools controladas y capa de seguridad por defecto.

## Tools disponibles

| Tool | Función | Control de seguridad |
|---|---|---|
| `fs_tool` | Leer/escribir archivos | Allowlist de paths |
| `web_tool` | Peticiones GET a la web | Allowlist de dominios, solo GET |
| `code_tool` | Ejecutar Python | Sandbox RestrictedPython + timeout 10s |
| `db_tool` | Consultar base de datos | Solo SELECT, path configurable |

## Inicio rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Ejecutar
python -m agent.main
```

## Con Docker

```bash
cp .env.example .env  # edita ANTHROPIC_API_KEY
cd docker && docker compose up --build
```

## Estructura

```
agent/
  main.py          ← entry point
  graph.py         ← nodos y edges LangGraph
  state.py         ← estado compartido
  tools/           ← fs, web, code, db
  sandbox/         ← ejecutor seguro de código
  audit/           ← log estructurado de acciones
config/            ← allowlists y manifest de tools
docker/            ← Dockerfile, compose, seccomp
wiki/              ← documentación extendida
```

## Documentación

Ver [wiki/](wiki/) para arquitectura, seguridad y guía de contribución.
