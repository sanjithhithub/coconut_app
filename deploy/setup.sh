#!/usr/bin/env bash

set -e  # Exit immediately if any command fails

PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'
PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev sqlite3 supervisor nginx git

echo "📂 Setting up project directory..."
if [ ! -d "$PROJECT_BASE_PATH" ]; then
    sudo mkdir -p "$PROJECT_BASE_PATH"
    sudo chown -R ubuntu:ubuntu "$PROJECT_BASE_PATH"
    echo "✔️ Directory created: $PROJECT_BASE_PATH"
else
    echo "✔️ Directory already exists: $PROJECT_BASE_PATH"
fi

# Clone repository if not already cloned
if [ ! -d "$PROJECT_BASE_PATH/.git" ]; then
    echo "📥 Cloning repository..."
    git clone "$PROJECT_GIT_URL" "$PROJECT_BASE_PATH"
else
    echo "✔️ Repository already cloned, pulling latest changes..."
    cd "$PROJECT_BASE_PATH" && git pull origin main
fi

# Check if the required files exist before proceeding
if [ ! -f "$PROJECT_BASE_PATH/requirements.txt" ]; then
    echo "❌ ERROR: requirements.txt not found in $PROJECT_BASE_PATH"
    exit 1
fi

if [ ! -f "$PROJECT_BASE_PATH/manage.py" ]; then
    echo "❌ ERROR: manage.py not found in $PROJECT_BASE_PATH"
    exit 1
fi

# Set up Python virtual environment
echo "🐍 Setting up virtual environment..."
cd "$PROJECT_BASE_PATH"
python3 -m venv env
source env/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt uwsgi==2.0.28

# Run database migrations
echo "⚙️ Running database migrations..."
python manage.py migrate

echo "✅ Migrations applied successfully!"
#!/bin/bash

set -e  # Exit on any error

PROJECT_BASE_PATH="/usr/local/apps/coconut_app"
SUPERVISOR_CONF="$PROJECT_BASE_PATH/deploy/supervisor_coconut_api.conf"

# ✅ Check if Supervisor config file exists
if [ ! -f "$SUPERVISOR_CONF" ]; then
    echo "❌ ERROR: Supervisor config file not found at $SUPERVISOR_CONF"
    exit 1
fi

# ✅ Copy the Supervisor config file
sudo cp "$SUPERVISOR_CONF" /etc/supervisor/conf.d/coconut_calculation.conf

# ✅ Set up Supervisor
echo "⚙️ Configuring Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_api || { echo "❌ Supervisor restart failed"; exit 1; }

echo "✅ Supervisor setup complete for coconut_calculation!"

# Check Nginx config file
NGINX_CONF="$PROJECT_BASE_PATH/deploy/nginx_coconut_api.conf"
if [ ! -f "$NGINX_CONF" ]; then
    echo "❌ ERROR: Nginx config file not found at $NGINX_CONF"
    exit 1
fi

# Set up Nginx
echo "🌍 Configuring Nginx..."
sudo cp "$NGINX_CONF" /etc/nginx/sites-available/coconut_api.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/coconut_api.conf /etc/nginx/sites-enabled/coconut_api.conf
sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }

echo "✅ Deployment Complete! 🎉"
