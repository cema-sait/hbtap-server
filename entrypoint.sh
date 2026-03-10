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

echo "Making migrations for app (newly added)..."
python manage.py makemigrations app --noinput

echo "Migrating app (newly added)..."
python manage.py migrate app --noinput

echo "Running remaining migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# --- Superuser creation (idempotent) ---
echo "Checking if superuser exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    print('Creating superuser...')
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    print('Superuser already exists, skipping creation.')
"

echo "Starting server..."
exec "$@"