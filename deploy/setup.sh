#!/usr/bin/env bash

set -e  # Exit script on error

# Set the GitHub repository URL
PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'
PROJECT_BASE_PATH='/usr/local/apps/coconut_api'

# Set Ubuntu Language
locale-gen en_GB.UTF-8

# Install required system packages
echo "🔄 Installing dependencies..."
sudo apt update && sudo apt install -y python3-pip python3-venv python3-dev sqlite3 supervisor nginx git

# Create project directory if it doesn't exist
echo "📂 Setting up project directory..."
if [ ! -d "$PROJECT_BASE_PATH" ]; then
    sudo mkdir -p "$PROJECT_BASE_PATH"
    sudo chown -R ubuntu:ubuntu "$PROJECT_BASE_PATH"
    echo "✔️ Directory created: $PROJECT_BASE_PATH"
else
    echo "✔️ Directory already exists: $PROJECT_BASE_PATH"
fi

# Clone the repository if not already cloned
if [ ! -d "$PROJECT_BASE_PATH/.git" ]; then
    git clone "$PROJECT_GIT_URL" "$PROJECT_BASE_PATH"
else
    echo "✔️ Repository already cloned, pulling latest changes..."
    cd "$PROJECT_BASE_PATH" && git pull origin main
fi

# Create and activate virtual environment
echo "🐍 Setting up virtual environment..."
cd "$PROJECT_BASE_PATH"
python3 -m venv env
source env/bin/activate

# Install project dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt uwsgi==2.0.28
else
    echo "❌ ERROR: requirements.txt not found!"
    exit 1
fi

# Run database migrations
echo "⚙️ Running database migrations..."
if [ -f "manage.py" ]; then
    python manage.py migrate
    echo "✅ Migrations applied successfully!"
else
    echo "❌ ERROR: manage.py not found!"
    exit 1
fi

# Verify if the Supervisor config exists
SUPERVISOR_CONF="$PROJECT_BASE_PATH/deploy/supervisor_coconut_api.conf"
if [ ! -f "$SUPERVISOR_CONF" ]; then
    echo "❌ ERROR: Supervisor config file not found at $SUPERVISOR_CONF"
    exit 1
fi

# Setup Supervisor
echo "⚙️ Configuring Supervisor..."
sudo cp "$SUPERVISOR_CONF" /etc/supervisor/conf.d/coconut_api.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_api || { echo "❌ Supervisor restart failed"; exit 1; }

# Verify if the Nginx config exists
NGINX_CONF="$PROJECT_BASE_PATH/deploy/nginx_coconut_api.conf"
if [ ! -f "$NGINX_CONF" ]; then
    echo "❌ ERROR: Nginx config file not found at $NGINX_CONF"
    exit 1
fi

# Setup Nginx
echo "🌍 Configuring Nginx..."
sudo cp "$NGINX_CONF" /etc/nginx/sites-available/coconut_api.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/coconut_api.conf /etc/nginx/sites-enabled/coconut_api.conf
sudo systemctl restart nginx || { echo "❌ Nginx restart failed"; exit 1; }

echo "✅ Deployment Complete! 🎉"
