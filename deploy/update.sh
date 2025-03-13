#!/usr/bin/env bash

set -e  # Exit immediately if any command fails

PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

echo "🔄 Pulling latest changes from GitHub..."
cd "$PROJECT_BASE_PATH"
git pull origin main

echo "⚙️ Applying database migrations..."
"$PROJECT_BASE_PATH/env/bin/python" manage.py migrate

echo "📂 Collecting static files..."
"$PROJECT_BASE_PATH/env/bin/python" manage.py collectstatic --noinput

echo "🚀 Restarting Supervisor process..."
sudo supervisorctl restart coconut_calculation

echo "✅ Update complete! 🎉"
