#!/bin/sh

set -e

cd /app

echo "==> Activate the Python virtual environment"
. .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate Python virtual environment"
    exit 1
fi

echo "==> Waiting for database"
# uv run python manage.py wait_for_postgresql

echo "==> Collect static files"
python manage.py collectstatic --noinput

echo "==> Migrations"
python manage.py makemigrations

echo "==> Migrate"
python manage.py migrate


echo "==> Run server with DEBUG=${DEBUG}"
LOG_LEVEL="--log-level info"

if [ "${DEBUG}" = "True" ]; then
    AUTO_RELOAD="--reload"
    LOG_LEVEL="--log-level debug"
fi

gunicorn core.wsgi \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    ${AUTO_RELOAD:-} \
    ${LOG_LEVEL:-}
