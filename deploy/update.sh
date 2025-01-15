#!/usr/bin/env bash

set -e  # Exit on any error

PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

# Navigate to the project directory
cd "$PROJECT_BASE_PATH" || { echo "Project directory not found: $PROJECT_BASE_PATH"; exit 1; }

# Pull the latest changes from the repository
echo "Pulling latest changes from Git..."
git pull || { echo "Git pull failed"; exit 1; }

# Activate the virtual environment
echo "Activating virtual environment..."
source "$PROJECT_BASE_PATH/env/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate || { echo "Database migration failed"; exit 1; }

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || { echo "Collectstatic failed"; exit 1; }

# Restart the application using Supervisor
echo "Restarting Supervisor-managed process..."
supervisorctl restart coconut_calculation || { echo "Supervisor restart failed"; exit 1; }

echo "Deployment complete! :)"
