# Arquitectura

## Flujo del agente

```
Usuario input
     ↓
  [Planner]          ← LLM decide qué tool usar (o responde directo)
     ↓
  [ToolNode]         ← ejecuta la tool seleccionada
     ↓
  [Auditor]          ← registra resultado antes de volver al planner
     ↓
  [Planner]          ← ¿necesita otra tool? → loop | No → output
```

## Nodos LangGraph

| Nodo | Archivo | Responsabilidad |
|---|---|---|
| `planner` | `graph.py` | Invoca al LLM con las tools disponibles |
| `tools` | LangGraph `ToolNode` | Ejecuta la tool elegida por el LLM |
| `auditor` | `graph.py` | Registra el resultado de la tool |

## Estado compartido (`AgentState`)

```python
messages      # historial de mensajes (HumanMessage, AIMessage, ToolMessage)
tool_calls    # registro de calls realizados en la sesión
current_tool  # tool activa en la iteración actual
tool_result   # resultado crudo de la última tool
audit_log     # lista de entradas de auditoría
iteration     # contador de ciclos del agente
error         # error capturado si existe
```

## Decisión de loop

`should_continue()` revisa si el último mensaje del LLM tiene `tool_calls`:
- **Sí** → va a `ToolNode` → `auditor` → `planner`
- **No** → `END` (respuesta final al usuario)
