# ═══════════════════════════════════════════════════════════════
#  ProjectForge 3D — Production Dockerfile
#  Runtime: Python 3.12 slim | ASGI: Daphne | Reverse proxy aware
# ═══════════════════════════════════════════════════════════════

FROM python:3.12-slim

# ── System dependencies ────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Non-root user (security best practice) ────────────────────
RUN groupadd --gid 1001 appgroup \
 && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# ── Python dependencies (layer cache friendly) ────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────
COPY --chown=appuser:appgroup . .

# ── Required directories ──────────────────────────────────────
RUN mkdir -p staticfiles media \
 && chown -R appuser:appgroup staticfiles media

# ── Entrypoint script ─────────────────────────────────────────
RUN chmod +x scripts/entrypoint.sh

# ── Switch to non-root user ───────────────────────────────────
USER appuser

# ── Port (Render injects $PORT at runtime) ────────────────────
EXPOSE 8000

# ── Default: production entrypoint ───────────────────────────
#    Workers override this via dockerCommand in render.yaml
CMD ["scripts/entrypoint.sh"]
