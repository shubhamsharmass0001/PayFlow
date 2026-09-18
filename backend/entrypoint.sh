#!/bin/bash
set -e

if [ "$1" = "uvicorn" ]; then
    echo "[PAYFLOW] Web backend starting — running Alembic database migrations..."
    alembic upgrade head

    if [ "${ENVIRONMENT:-development}" = "development" ]; then
        echo "[PAYFLOW] Environment is development — running automated data seeding..."
        python -m seed.seed_data || echo "[PAYFLOW] Seeding step complete."
    fi
fi

echo "[PAYFLOW] Starting service: $@"
exec "$@"
