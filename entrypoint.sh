#!/bin/sh

echo "Waiting for database..."

while ! python -c "
import psycopg2
import os
from urllib.parse import urlparse

url = os.environ['DATABASE_URL']
parsed = urlparse(url)

conn = psycopg2.connect(
    dbname=parsed.path.lstrip('/'),
    user=parsed.username,
    password=parsed.password,
    host=parsed.hostname,
    port=parsed.port
)
conn.close()
"; do
  sleep 2
done

echo "Database is up."

echo "Running migrations..."
alembic upgrade head

echo "Starting app..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}