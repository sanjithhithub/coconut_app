#!/bin/bash

set -e

PROJECT_BASE_PATH="/usr/local/apps/coconut_api"

echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev build-essential \
                    nginx supervisor git curl libpcre3 libpcre3-dev \
                    zlib1g-dev uwsgi uwsgi-plugin-python3

echo "📂 Setting up project directory..."
if [ ! -d "$PROJECT_BASE_PATH" ]; then
    sudo mkdir -p "$PROJECT_BASE_PATH"
    echo "✔️ Directory created at $PROJECT_BASE_PATH"
fi

# Change ownership only if the directory exists
if [ -d "$PROJECT_BASE_PATH" ]; then
    sudo chown -R ubuntu:ubuntu "$PROJECT_BASE_PATH"
    echo "✔️ Ownership changed for $PROJECT_BASE_PATH"
else
    echo "❌ Failed to create directory: $PROJECT_BASE_PATH"
    exit 1
fi

echo "🐍 Setting up virtual environment..."
cd "$PROJECT_BASE_PATH"
python3 -m venv env
source env/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️ Configuring Supervisor..."
if [ -f "$PROJECT_BASE_PATH/deploy/supervisor_coconut_api.conf" ]; then
    sudo cp "$PROJECT_BASE_PATH/deploy/supervisor_coconut_api.conf" /etc/supervisor/conf.d/coconut_api.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart coconut_api || { echo "❌ Supervisor restart failed"; exit 1; }
else
    echo "❌ Supervisor config not found!"
    exit 1
fi

echo "🌍 Configuring Nginx..."
if [ -f "$PROJECT_BASE_PATH/deploy/nginx_coconut_api.conf" ]; then
    sudo cp "$PROJECT_BASE_PATH/deploy/nginx_coconut_api.conf" /etc/nginx/sites-available/coconut_api.conf
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/coconut_api.conf /etc/nginx/sites-enabled/coconut_api.conf
    sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }
else
    echo "❌ Nginx config not found!"
    exit 1
fi

echo "✅ Setup Complete! 🎉"
