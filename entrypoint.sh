#!/bin/sh
set -e

echo "Making migrations for users..."
python manage.py makemigrations users --noinput

echo "Migrating users..."
python manage.py migrate users --noinput

echo "Making migrations for members..."
python manage.py makemigrations members --noinput

echo "Migrating members..."
python manage.py migrate members --noinput

echo "Running remaining migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
