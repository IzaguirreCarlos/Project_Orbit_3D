#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  ProjectForge 3D — Production Entrypoint
#  Orden: migrate → collectstatic → daphne
# ═══════════════════════════════════════════════════════════════
set -e

echo "──────────────────────────────────────────"
echo "  ProjectForge 3D — Starting up"
echo "  ENV: ${DJANGO_SETTINGS_MODULE}"
echo "  PORT: ${PORT:-8000}"
echo "──────────────────────────────────────────"

echo "[1/3] Applying database migrations..."
python manage.py migrate --no-input

echo "[2/3] Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "[3/3] Starting Daphne ASGI server..."
exec daphne \
  -b 0.0.0.0 \
  -p "${PORT:-8000}" \
  --proxy-headers \
  config.asgi:application
