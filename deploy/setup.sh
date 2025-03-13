#!/usr/bin/env bash

set -e  # Exit on any error

PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'
PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

echo "🔄 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev sqlite3 supervisor nginx git uwsgi uwsgi-plugin-python3

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

echo "🐍 Setting up virtual environment..."
cd "$PROJECT_BASE_PATH"
python3 -m venv env
source env/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt uwsgi==2.0.28

echo "⚙️ Running database migrations..."
python manage.py migrate

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# ✅ Configure Supervisor
SUPERVISOR_CONF="$PROJECT_BASE_PATH/deploy/supervisor_coconut_api.conf"
if [ -f "$SUPERVISOR_CONF" ]; then
    echo "⚙️ Configuring Supervisor..."
    sudo cp "$SUPERVISOR_CONF" /etc/supervisor/conf.d/coconut_calculation.conf
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl restart coconut_calculation || { echo "❌ Supervisor restart failed"; exit 1; }
else
    echo "❌ ERROR: Supervisor config not found!"
    exit 1
fi

# ✅ Configure Nginx
NGINX_CONF="$PROJECT_BASE_PATH/deploy/nginx_coconut_api.conf"
if [ -f "$NGINX_CONF" ]; then
    echo "🌍 Configuring Nginx..."
    sudo cp "$NGINX_CONF" /etc/nginx/sites-available/coconut_api.conf
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo ln -sf /etc/nginx/sites-available/coconut_api.conf /etc/nginx/sites-enabled/coconut_api.conf
    sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }
else
    echo "❌ ERROR: Nginx config not found!"
    exit 1
fi

echo "✅ Setup Complete! 🎉"
