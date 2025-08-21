#!/usr/bin/env bash
# Render.com build script for Tank Asset Management API
set -o errexit  # exit on error

echo "🚀 Starting Render build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create required directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p static/uploads/farm_layouts
mkdir -p staticfiles

# Set Django settings for production
export DJANGO_SETTINGS_MODULE=config.settings_production

# Collect static files
echo "🔧 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

echo "✅ Build process completed successfully!"
echo "🌐 Your Tank Asset Management API is ready for deployment!"

# Optional: Create superuser if environment variables are set
if [[ -n "${DJANGO_SUPERUSER_USERNAME}" && -n "${DJANGO_SUPERUSER_EMAIL}" && -n "${DJANGO_SUPERUSER_PASSWORD}" ]]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput
    echo "✅ Superuser created successfully!"
else
    echo "ℹ️ Superuser not created. Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD to create one automatically."
fi