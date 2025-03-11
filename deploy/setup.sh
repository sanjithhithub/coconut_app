#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'

PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

# Set Ubuntu Language
apt-get install -y locales || { echo "Locales installation failed"; exit 1; }
locale-gen en_GB.UTF-8

# Install dependencies
echo "Installing dependencies..."
apt-get update || { echo "apt-get update failed"; exit 1; }
apt-get install -y python3-dev python3-venv sqlite3 python3-pip supervisor nginx git || { echo "Dependencies installation failed"; exit 1; }

# Create project directory and clone the repository
mkdir -p $PROJECT_BASE_PATH || { echo "Directory creation failed"; exit 1; }
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH || { echo "Git clone failed"; exit 1; }

# Create a Python virtual environment
python3 -m venv $PROJECT_BASE_PATH/env || { echo "Virtual environment creation failed"; exit 1; }

# Install Python dependencies
if [ ! -f "$PROJECT_BASE_PATH/requirements.txt" ]; then
    echo "requirements.txt not found!"
    exit 1
fi
$PROJECT_BASE_PATH/env/bin/pip install -r $PROJECT_BASE_PATH/requirements.txt uWSGI==2.0.28 || { echo "Dependencies installation failed"; exit 1; }

# Run database migrations
$PROJECT_BASE_PATH/env/bin/python $PROJECT_BASE_PATH/manage.py migrate || { echo "Database migration failed"; exit 1; }

# Setup Supervisor to run the uWSGI process
if [ ! -f "$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf" ]; then
    echo "Supervisor config not found!"
    exit 1
fi
cp $PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf /etc/supervisor/conf.d/coconut_calculation.conf
supervisorctl reread || { echo "Supervisor reread failed"; exit 1; }
supervisorctl update || { echo "Supervisor update failed"; exit 1; }
supervisorctl restart coconut_calculation || { echo "Supervisor restart failed"; exit 1; }

# Setup Nginx to make the application accessible
if [ ! -f "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" ]; then
    echo "Nginx config not found!"
    exit 1
fi
cp $PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf /etc/nginx/sites-available/coconut_calculation.conf
rm /etc/nginx/sites-enabled/default || true
ln -s /etc/nginx/sites-available/coconut_calculation.conf /etc/nginx/sites-enabled/coconut_calculation.conf
systemctl restart nginx.service || { echo "Nginx restart failed"; exit 1; }

echo "DONE! :)"
