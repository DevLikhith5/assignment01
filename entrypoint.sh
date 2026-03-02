#!/bin/sh

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! python -c "import psycopg2; psycopg2.connect(host='db', dbname='credit_db', user='postgres', password='postgres')" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py migrate

echo "Ingesting data..."
python manage.py ingest_data || echo "Data ingestion failed or depends on missing setup, continuing anyway..."

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
