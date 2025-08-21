#!/usr/bin/env bash
# exit on error
set -o errexit

# Create logs directory
mkdir -p logs

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate