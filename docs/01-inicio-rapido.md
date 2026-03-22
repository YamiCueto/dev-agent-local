# Inicio rápido

## 1. Requisitos previos

- Python 3.12+
- [Ollama](https://ollama.com) corriendo localmente
- MySQL o MariaDB corriendo en `localhost:3306`
- Modelo `llama3.1:8b` descargado en Ollama

```bash
# Verificar Ollama
curl http://localhost:11434/api/tags

# Descargar el modelo si no lo tienes
ollama pull llama3.1:8b
```

## 2. Clonar e instalar

```bash
git clone https://github.com/YamiCueto/dev-agent-local.git
cd dev-agent-local

pip install -r requirements.txt
```

## 3. Configurar variables de entorno

```bash
# Windows
set OLLAMA_MODEL=llama3.1:8b
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=
set MYSQL_DB=dev_agent

# Linux / Mac
export OLLAMA_MODEL=llama3.1:8b
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=
export MYSQL_DB=dev_agent
```

> La base de datos `dev_agent` se crea automáticamente en el primer arranque.

## 4. Ejecutar

```bash
python -m agent.main
```

### Primera ejecución (sin sesiones previas)

```
Dev Agent Local — escribe 'salir' para terminar, 'nueva' para cambiar sesión

Nueva sesión: a1b2c3d4...

>>>
```

### Ejecuciones siguientes (con sesiones guardadas)

```
Dev Agent Local — escribe 'salir' para terminar, 'nueva' para cambiar sesión

Sesiones anteriores:
  [1] cuantas sesiones tengo guardadas  —  2026-03-22 17:59
  [2] cuanto es 7 al cuadrado          —  2026-03-22 17:56
  [n] Nueva sesión

Elige sesión >>>
```

## 5. Comandos del REPL

| Comando | Acción |
|---|---|
| Cualquier texto | Envía mensaje al agente |
| `nueva` | Abre el selector de sesiones |
| `salir` / `exit` / `quit` | Cierra el agente |
| `Ctrl+C` | Cierra el agente |
