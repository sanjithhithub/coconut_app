#!/bin/bash

# Exit script on any error
set -e

echo "Activating virtual environment..."
source /usr/local/apps/coconut_app/env/bin/activate

echo "Pulling latest changes from Git..."
cd /usr/local/apps/coconut_app
git pull origin main

echo "Installing updated dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Restarting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart coconut_calculation
sudo systemctl restart nginx

echo "Update completed successfully!"
