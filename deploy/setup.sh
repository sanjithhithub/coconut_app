#!/bin/bash

# Exit on any error
set -e

# Define the project path
PROJECT_BASE_PATH="/usr/local/apps/coconut_app"

echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing required packages..."
sudo apt install -y python3-pip python3-venv python3-dev build-essential \
                    nginx supervisor git curl libpcre3 libpcre3-dev \
                    zlib1g-dev uwsgi uwsgi-plugin-python3

echo "📂 Setting up project directory..."
if [ ! -d "$PROJECT_BASE_PATH" ]; then
    sudo mkdir -p "$PROJECT_BASE_PATH"
    sudo chown -R ubuntu:ubuntu "$PROJECT_BASE_PATH"
fi

echo "📥 Cloning repository..."
cd "$PROJECT_BASE_PATH"
if [ ! -d "$PROJECT_BASE_PATH/.git" ]; then
    git clone https://github.com/sanjithhithub/coconut_app.git "$PROJECT_BASE_PATH"
else
    echo "✔️ Repository already cloned, pulling latest changes..."
    git pull origin main
fi

echo "🐍 Setting up virtual environment..."
python3 -m venv env
source env/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Configuring uWSGI..."
cat <<EOL | sudo tee /usr/local/apps/coconut_app/uwsgi.ini
[uwsgi]
chdir = /usr/local/apps/coconut_app
module = coconut_app.wsgi:application
home = /usr/local/apps/coconut_app/env
socket = /run/uwsgi/coconut_calculation.sock
chmod-socket = 666
vacuum = true
master = true
processes = 4
threads = 2
daemonize = /var/log/uwsgi/coconut_calculation.log
EOL

echo "⚙️ Configuring Supervisor..."
if [ -f "$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf" ]; then
    sudo cp "$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf" /etc/supervisor/conf.d/coconut_calculation.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart coconut_calculation || { echo "❌ Supervisor restart failed"; exit 1; }
else
    echo "❌ Supervisor config not found!"
    exit 1
fi

echo "🌍 Configuring Nginx..."
if [ -f "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" ]; then
    sudo cp "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" /etc/nginx/sites-available/coconut_calculation
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/coconut_calculation /etc/nginx/sites-enabled/
    sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }
else
    echo "❌ Nginx config not found!"
    exit 1
fi

echo "✅ Setup complete! 🎉"
