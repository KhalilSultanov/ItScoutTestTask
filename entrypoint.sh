#!/bin/bash
set -e

./wait-for-it.sh postgres:5432 --timeout=30

echo "Running migrations..."
python manage.py migrate

echo "Running tests..."
pytest -v

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
