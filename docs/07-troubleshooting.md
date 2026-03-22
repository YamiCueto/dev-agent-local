# Troubleshooting

## El agente no responde / timeout

**Síntoma:** El prompt `>>>` aparece pero el agente no contesta.

**Causas y soluciones:**

```bash
# 1. Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# 2. Verificar que el modelo está descargado
ollama list

# 3. Si el modelo no aparece, descargarlo
ollama pull llama3.1:8b
```

---

## El agente no usa la tool correcta

**Síntoma:** El agente responde desde su conocimiento en vez de ejecutar una tool.

**Causa:** El modelo no generó `tool_calls` estructurados — puede ser un modelo sin soporte de tool calling.

**Solución:** Cambiar al modelo recomendado:

```bash
set OLLAMA_MODEL=llama3.1:8b
python -m agent.main
```

Ver [05-configuracion.md](05-configuracion.md) para lista de modelos compatibles.

---

## ERROR: path no está en la allowlist

**Síntoma:**
```
ERROR: path no está en la allowlist de lectura.
```

**Causa:** El modelo generó un path absoluto (`/README.md`) en vez de relativo (`./README.md`).

**Solución 1 (usuario):** Reformular el prompt siendo explícito:
```
>>> lee el archivo ./README.md
```

**Solución 2 (config):** Agregar el path a `config/allowed_paths.yml`:
```yaml
allowed_paths:
  read:
    - .
    - /ruta/que/necesitas
```

---

## ImportError: __import__ not found

**Síntoma:**
```
ERROR: ImportError: __import__ not found
```

**Causa:** El código que el agente intenta ejecutar usa `import` — bloqueado por RestrictedPython.

**Comportamiento esperado** — la sandbox está funcionando correctamente. El agente no debe importar módulos externos.

---

## SandboxTimeoutError: execution exceeded 10s

**Síntoma:**
```
ERROR: SandboxTimeoutError: execution exceeded 10s
```

**Causa:** El código generado por el agente tiene un loop infinito o es demasiado lento.

**Solución:** El timeout está en `agent/sandbox/executor.py`:
```python
TIMEOUT_SECONDS = 10   # aumentar si necesitas más tiempo
```

---

## Error de conexión a MySQL

**Síntoma:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")
```

**Verificar:**
```bash
# Windows — verificar que MySQL está corriendo
sc query MySQL80

# Probar conexión
python -c "import pymysql; pymysql.connect(host='localhost', user='root', password='')"
```

**Variables de entorno a revisar:**
```bash
echo %MYSQL_HOST%
echo %MYSQL_USER%
echo %MYSQL_PASSWORD%
```

---

## Caracteres extraños en la consola (Windows)

**Síntoma:** Aparecen `?` o `â€` en lugar de tildes y ñ.

**Causa:** La consola Windows no estaba en UTF-8.

**Solución:** El agente fuerza UTF-8 automáticamente en Windows. Si persiste:
```cmd
chcp 65001
python -m agent.main
```

---

## La sesión no se guarda / no aparece en la lista

**Síntoma:** Al reiniciar, las sesiones anteriores no aparecen.

**Verificar en MySQL:**
```sql
USE dev_agent;
SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC;
```

Si la tabla no existe:
```python
from agent.persistence.mysql_store import init_db
init_db()
```

---

## El agente entra en loop infinito de tool calls

**Síntoma:** El agente llama tools repetidamente sin dar respuesta final.

**Causa:** El modelo interpreta el resultado de la tool como señal de que necesita otra.

**Verificar** en el audit log:
```bash
tail -20 /tmp/agent-audit/audit.jsonl
```

**Solución temporal:** `Ctrl+C` para interrumpir. El estado actual **ya está guardado** en MySQL hasta el último turno completo.
