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
if [ -f "$PROJECT_BASE_PATH/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$PROJECT_BASE_PATH/requirements.txt"
else
    echo "❌ requirements.txt not found in $PROJECT_BASE_PATH"
    exit 1
fi

echo "🗄️ Running database migrations..."
if [ -f "$PROJECT_BASE_PATH/manage.py" ]; then
    python manage.py makemigrations
    python manage.py migrate
else
    echo "❌ manage.py not found in $PROJECT_BASE_PATH"
    exit 1
fi

echo "✅ Setup Complete! 🎉"
