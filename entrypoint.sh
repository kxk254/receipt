#!/bin/bash
set -e

echo "Collecting static files"
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Setting up permission..."
mkdir -p /receipt/db/db_backups
chown -R 101:101 /receipt/staticfiles /receipt/db

echo "Starting Gunicorn..."
exec gunicorn ocr_v1.wsgi:application --bind 0.0.0.0:8000 --workers 5