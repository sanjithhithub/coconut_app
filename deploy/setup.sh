#!/bin/bash

# Exit script on any error
set -e

echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "Installing required packages..."
sudo apt install -y python3-pip python3-venv python3-dev build-essential \
                    nginx supervisor git curl libpcre3 libpcre3-dev \
                    zlib1g-dev

echo "Setting up project directory..."
PROJECT_DIR="/usr/local/apps/coconut_app"
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown -R ubuntu:ubuntu "$PROJECT_DIR"
fi

echo "Cloning repository..."
cd "$PROJECT_DIR"
if [ ! -d "$PROJECT_DIR/.git" ]; then
    git clone https://github.com/sanjithhithub/coconut_app.git "$PROJECT_DIR"
else
    echo "Repository already cloned, pulling latest changes..."
    git pull origin main
fi

echo "Setting up virtual environment..."
python3 -m venv env
source env/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Configuring Supervisor..."
sudo cp /mnt/data/supervisor_coconut_calculation.conf /etc/supervisor/conf.d/coconut_calculation.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_calculation

echo "Configuring Nginx..."
sudo cp /mnt/data/nginx_coconut_calculation.conf /etc/nginx/sites-available/coconut_calculation
sudo ln -sf /etc/nginx/sites-available/coconut_calculation /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "Setup complete!"
