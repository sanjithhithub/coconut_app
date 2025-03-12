#!/usr/bin/env bash

set -e

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'

PROJECT_BASE_PATH='/usr/local/apps/coconut_api'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install Python, SQLite, pip, and dependencies
echo "Installing dependencies..."
apt-get update
sudo apt update && sudo apt install -y python3-pip python3-venv python3-dev sqlite3 supervisor nginx git

mkdir -p $PROJECT_BASE_PATH
git clone $PROJECT_GIT_URL $PROJECT_BASE_PATH

python3 -m venv $PROJECT_BASE_PATH/env

$PROJECT_BASE_PATH/env/bin/pip install -r $PROJECT_BASE_PATH/requirements.txt uwsgi==2.0.28

# Run migrations
$PROJECT_BASE_PATH/env/bin/python $PROJECT_BASE_PATH/manage.py migrate

echo "migrate sucessfully :)"

# Verify if the Supervisor config exists
if [ ! -f "$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf" ]; then
    echo "❌ ERROR: Supervisor config file not found at $PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf"
    exit 1
fi

# Setup Supervisor
cp $PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf /etc/supervisor/conf.d/coconut_api.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_api  # Ensure the correct process name

# Setup nginx to make our application accessible.
cp $PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf /etc/nginx/sites-available/coconut_api.conf
rm /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/coconut_ap.conf /etc/nginx/sites-enabled/coconut_app.conf
systemctl restart nginx.service

echo "DONE! :)"
