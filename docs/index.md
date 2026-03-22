# Dev Agent Local — Documentación

Agente de desarrollo local con **LangGraph** + **Ollama**, 4 tools controladas, sandbox de código, persistencia de sesiones en MySQL y audit log estructurado.

---

## Contenido

| Documento | Descripción |
|---|---|
| [01-inicio-rapido.md](01-inicio-rapido.md) | Instalación y primera ejecución |
| [02-arquitectura.md](02-arquitectura.md) | Diagrama del sistema y flujo del agente |
| [03-sesiones.md](03-sesiones.md) | Persistencia de sesiones con MySQL |
| [04-tools-referencia.md](04-tools-referencia.md) | Referencia completa de las 4 tools |
| [05-configuracion.md](05-configuracion.md) | Variables de entorno y archivos de config |
| [06-seguridad.md](06-seguridad.md) | Modelo de seguridad por capas |
| [07-troubleshooting.md](07-troubleshooting.md) | Problemas comunes y soluciones |

---

## Requisitos mínimos

| Componente | Versión mínima |
|---|---|
| Python | 3.12+ |
| Ollama | Cualquier versión reciente |
| MySQL / MariaDB | 8.0+ / 10.6+ |
| Modelo con tool calling | `llama3.1:8b` (recomendado) |
