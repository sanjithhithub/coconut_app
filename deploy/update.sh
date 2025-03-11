#!/bin/bash

# Exit script on any error
set -e

echo "Activating virtual environment..."
if [ -d "/usr/local/apps/coconut_app/env" ]; then
    source /usr/local/apps/coconut_app/env/bin/activate
else
    echo "Virtual environment not found!"
    exit 1
fi

echo "Pulling latest changes from Git..."
cd /usr/local/apps/coconut_app
git pull origin main || { echo "Git pull failed!"; exit 1; }

echo "Installing updated dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi

echo "Restarting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_calculation
sudo systemctl restart nginx

echo "Update completed successfully!"