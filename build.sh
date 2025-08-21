#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating directories..."
mkdir -p staticfiles
mkdir -p media

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --settings=config.settings_production

echo "Running migrations..."
python manage.py migrate --settings=config.settings_production

echo "Creating superuser..."
python manage.py createsuperuser --noinput --settings=config.settings_production || true

echo "Build completed!"