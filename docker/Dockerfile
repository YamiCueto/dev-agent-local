# ── Stage 1: builder ──────────────────────────────────────────────────────────
# gcc solo vive aquí para compilar extensiones C de los paquetes (ej: PyYAML).
# Esta capa no llega a la imagen final.
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
# Imagen limpia: solo Python + los paquetes ya compilados. Sin gcc.
FROM python:3.12-slim

WORKDIR /app

# Copiar paquetes compilados desde el builder
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY . .

# Usuario no-root
RUN useradd -m -u 1000 agentuser \
    && chown -R agentuser:agentuser /app /tmp

USER agentuser

RUN mkdir -p /tmp/agent-workspace /tmp/agent-audit

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "agent.main"]
