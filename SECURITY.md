# Modelo de seguridad

## Principios

1. **Allowlist sobre blacklist** — solo lo explícitamente permitido funciona
2. **Menor privilegio** — cada tool tiene acceso mínimo necesario
3. **Audit trail** — toda acción queda en log estructurado antes de responder
4. **Sandbox para código** — ningún código llega al sistema sin pasar por RestrictedPython
5. **Read-only por defecto** — db_tool y web_tool son de solo lectura

## Por tool

### fs_tool
- Paths permitidos declarados en `config/allowed_paths.yml`
- Patrones denegados (`.env`, `*.key`, `*secret*`) aplicados antes del path check
- Escritura solo en `/tmp/agent-workspace`

### web_tool
- Dominios permitidos en `config/allowed_domains.yml`
- Solo método GET — no POST, PUT, DELETE, PATCH
- Timeout de 10 segundos por request

### code_tool
- `RestrictedPython` bloquea imports peligrosos, acceso a `__import__`, `open`, `exec`
- Timeout de 10 segundos via `SIGALRM`
- Output limitado a lo que `PrintCollector` capture

### db_tool
- Regex valida que la query empiece con `SELECT`
- Conexión en modo `ro` (SQLite read-only URI)
- Máximo 50 filas por query

## Contenedor Docker

- Usuario no-root (`agentuser`, uid 1000)
- `cap_drop: ALL`
- `no-new-privileges: true`
- Perfil seccomp en `docker/seccomp-profile.json`
- Volúmenes separados para workspace y audit logs
