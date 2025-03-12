#!/bin/bash

# Exit on any error
set -e

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

# ✅ Setup uWSGI configuration
echo "⚙️ Configuring uWSGI..."
UWSGI_CONF="$PROJECT_BASE_PATH/uwsgi.ini"
if [ ! -f "$UWSGI_CONF" ]; then
    echo "Creating uWSGI config file..."
    cat <<EOF | sudo tee "$UWSGI_CONF"
[uwsgi]
chdir = $PROJECT_BASE_PATH
module = coconut_app.wsgi:application
home = $PROJECT_BASE_PATH/env
socket = /run/uwsgi/coconut_app.sock
chmod-socket = 664
vacuum = true
die-on-term = true
processes = 4
threads = 2
EOF
fi
sudo chmod 644 "$UWSGI_CONF"

# ✅ Setup Supervisor to run the uWSGI process
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

# ✅ Setup Nginx to serve the application
echo "🌍 Configuring Nginx..."
if [ -f "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" ]; then
    sudo cp "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" /etc/nginx/sites-available/coconut_calculation.conf
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/coconut_calculation.conf /etc/nginx/sites-enabled/coconut_calculation.conf
    sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }
else
    echo "❌ Nginx config not found!"
    exit 1
fi

echo "✅ DONE! Setup complete. 🎉"
