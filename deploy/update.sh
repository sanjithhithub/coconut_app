#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status

# Define project base path
PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

# Change to project directory
if [ ! -d "$PROJECT_BASE_PATH" ]; then
    echo "ERROR: Project directory $PROJECT_BASE_PATH does not exist."
    exit 1
fi

cd "$PROJECT_BASE_PATH"

# Pull the latest code from the repository
echo "Pulling the latest code..."
if git pull; then
    echo "Code updated successfully."
else
    echo "ERROR: Failed to pull the latest code."
    exit 1
fi

# Activate the virtual environment
if [ ! -f "$PROJECT_BASE_PATH/env/bin/activate" ]; then
    echo "ERROR: Virtual environment not found. Ensure the environment is correctly set up."
    exit 1
fi

source "$PROJECT_BASE_PATH/env/bin/activate"

# Apply database migrations
echo "Applying database migrations..."
if python manage.py migrate; then
    echo "Database migrations applied successfully."
else
    echo "ERROR: Failed to apply database migrations."
    deactivate
    exit 1
fi

# Collect static files
echo "Collecting static files..."
if python manage.py collectstatic --noinput; then
    echo "Static files collected successfully."
else
    echo "ERROR: Failed to collect static files."
    deactivate
    exit 1
fi

# Restart Supervisor process
echo "Restarting Supervisor process..."
if supervisorctl restart coconut_calculation; then
    echo "Supervisor process restarted successfully."
else
    echo "ERROR: Failed to restart Supervisor process."
    deactivate
    exit 1
fi

# Deactivate the virtual environment
deactivate

echo "DONE! :)"
exit 0
