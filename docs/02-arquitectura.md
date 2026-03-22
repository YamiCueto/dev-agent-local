# Arquitectura

## Visión general del sistema

```mermaid
graph TB
    subgraph Usuario
        CLI["REPL — agent/main.py"]
    end

    subgraph Persistencia
        MySQL[(MySQL\ndev_agent.sessions)]
    end

    subgraph Agente["Agente LangGraph — agent/graph.py"]
        Planner["Planner\nChatOllama llama3.1:8b"]
        ToolNode["ToolNode\n(LangGraph prebuilt)"]
        Auditor["Auditor\nlog estructurado"]
    end

    subgraph Tools["agent/tools/"]
        fs["fs_read / fs_write"]
        web["web_search"]
        code["code_exec"]
        db["db_query"]
    end

    subgraph Sandbox["agent/sandbox/"]
        RestrictedPy["RestrictedPython 8.x\n+ ThreadPoolExecutor timeout"]
    end

    subgraph Audit["agent/audit/"]
        JSONL["/tmp/agent-audit/audit.jsonl"]
    end

    CLI -->|"carga historial"| MySQL
    CLI -->|"input usuario"| Planner
    Planner -->|"tool_calls"| ToolNode
    Planner -->|"sin tool_calls"| CLI
    ToolNode --> fs & web & db
    ToolNode --> code --> RestrictedPy
    ToolNode --> Auditor
    Auditor --> JSONL
    Auditor --> Planner
    CLI -->|"guarda sesión"| MySQL
```

## Flujo de un turno completo

```mermaid
sequenceDiagram
    actor U as Usuario
    participant M as main.py
    participant MySQL
    participant G as LangGraph
    participant LLM as Ollama llama3.1:8b
    participant T as Tool
    participant A as Auditor

    U->>M: escribe mensaje
    M->>MySQL: carga historial (si sesión activa)
    M->>G: graph.invoke({messages, ...})
    G->>LLM: planner — invoke con system prompt
    LLM-->>G: AIMessage con tool_calls
    G->>T: ejecuta tool seleccionada
    T-->>G: ToolMessage con resultado
    G->>A: auditor — registra en JSONL
    A-->>G: continúa
    G->>LLM: planner — ¿necesita otra tool?
    LLM-->>G: AIMessage sin tool_calls (respuesta final)
    G-->>M: result["messages"]
    M->>MySQL: save_session(thread_id, messages)
    M-->>U: imprime respuesta
```

## Nodos del grafo LangGraph

```mermaid
stateDiagram-v2
    [*] --> planner
    planner --> tools : tiene tool_calls
    planner --> [*] : sin tool_calls (END)
    tools --> auditor
    auditor --> planner
```

## Estado compartido (`AgentState`)

```python
class AgentState(TypedDict):
    messages    # historial completo (Human + AI + Tool messages)
    tool_calls  # calls realizados en la sesión actual
    current_tool
    tool_result
    audit_log   # entradas del auditor en este turno
    iteration   # contador de ciclos
    error
```

## Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Orquestación | LangGraph 1.0 |
| LLM | Ollama — llama3.1:8b (local) |
| Sandbox código | RestrictedPython 8.x + ThreadPoolExecutor |
| Persistencia | MySQL / MariaDB via pymysql |
| HTTP tools | httpx |
| Config | YAML + variables de entorno |
