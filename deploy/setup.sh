#!/usr/bin/env bash

set -e

# Set Git Repository URL
PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'
PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

# Set Ubuntu Language
echo "Setting up system locale..."
locale-gen en_GB.UTF-8 || { echo "Locale setup failed"; exit 1; }

# Install dependencies
echo "Updating and installing dependencies..."
apt-get update || { echo "apt-get update failed"; exit 1; }
apt-get install -y git python3-dev python3-venv sqlite3 python3-pip supervisor nginx || { echo "Dependencies installation failed"; exit 1; }

# Create project directory and clone the repository
echo "Setting up project directory..."
mkdir -p $PROJECT_BASE_PATH || { echo "Directory creation failed"; exit 1; }
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH || { echo "Git clone failed"; exit 1; }

# Create a Python virtual environment
echo "Creating virtual environment..."
python3 -m venv $PROJECT_BASE_PATH/env || { echo "Virtual environment creation failed"; exit 1; }

# Install Python dependencies
if [ ! -f "$PROJECT_BASE_PATH/requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi
echo "Installing Python dependencies..."
$PROJECT_BASE_PATH/env/bin/pip install -r $PROJECT_BASE_PATH/requirements.txt uwsgi==2.0.21 || { echo "Dependencies installation failed"; exit 1; }

# Run database migrations
echo "Running database migrations..."
$PROJECT_BASE_PATH/env/bin/python $PROJECT_BASE_PATH/manage.py migrate || { echo "Database migration failed"; exit 1; }

# Setup Supervisor for the uWSGI process
SUPERVISOR_CONF="$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf"
if [ ! -f "$SUPERVISOR_CONF" ]; then
    echo "Error: Supervisor config not found!"
    exit 1
fi
echo "Configuring Supervisor..."
cp $SUPERVISOR_CONF /etc/supervisor/conf.d/coconut_calculation.conf
supervisorctl reread || { echo "Supervisor reread failed"; exit 1; }
supervisorctl update || { echo "Supervisor update failed"; exit 1; }
supervisorctl restart coconut_calculation || { echo "Supervisor restart failed"; exit 1; }

# Setup Nginx
NGINX_CONF="$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf"
if [ ! -f "$NGINX_CONF" ]; then
    echo "Error: Nginx config not found!"
    exit 1
fi
echo "Configuring Nginx..."
cp $NGINX_CONF /etc/nginx/sites-available/coconut_calculation.conf
rm -f /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/coconut_calculation.conf /etc/nginx/sites-enabled/coconut_calculation.conf
systemctl reload nginx || { echo "Nginx reload failed"; exit 1; }

echo "Deployment Completed Successfully! 🎉"
