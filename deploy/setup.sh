#!/usr/bin/env bash

set -e  # Exit immediately if a command exits with a non-zero status

# TODO: Set to URL of git repo.
PROJECT_GIT_URL='https://github.com/sanjithhithub/coconut_app.git'

PROJECT_BASE_PATH='/usr/local/apps/coconut_app'

# Update system and install dependencies
echo "Updating system and installing dependencies..."
apt-get update -y && apt-get upgrade -y

# Install specific versions of packages
echo "Installing specific package versions..."
apt-get install -y python3=3.8.10-0ubuntu1~20.04 python3-dev python3-venv sqlite3 libsqlite3-dev python3-pip=20.0.2-5ubuntu1.8 supervisor=4.2.2-1ubuntu1 nginx=1.18.0-0ubuntu1 git locales

# Set Ubuntu locale (for language settings)
echo "Setting system locale..."
locale-gen en_GB.UTF-8
update-locale LANG=en_GB.UTF-8

# Create project base directory
echo "Setting up project directory..."
mkdir -p "$PROJECT_BASE_PATH"

# Clone the project from the Git repository
echo "Cloning project repository..."
if [ ! -d "$PROJECT_BASE_PATH/.git" ]; then
    git clone "$PROJECT_GIT_URL" "$PROJECT_BASE_PATH"
else
    echo "Repository already cloned. Pulling latest changes..."
    git -C "$PROJECT_BASE_PATH" pull
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv "$PROJECT_BASE_PATH/env"

# Install Python dependencies with specific versions
echo "Installing Python dependencies..."
"$PROJECT_BASE_PATH/env/bin/pip" install --upgrade pip==20.3.4
"$PROJECT_BASE_PATH/env/bin/pip" install -r "$PROJECT_BASE_PATH/requirements.txt" uwsgi==2.0.20  # Downgrade uwsgi

# Run database migrations
echo "Running database migrations..."
"$PROJECT_BASE_PATH/env/bin/python" "$PROJECT_BASE_PATH/manage.py" migrate

# Set up Supervisor configuration
echo "Configuring Supervisor..."
SUPERVISOR_CONF_PATH="/etc/supervisor/conf.d/coconut_calculation.conf"
cp "$PROJECT_BASE_PATH/deploy/supervisor_coconut_calculation.conf" "$SUPERVISOR_CONF_PATH"
supervisorctl reread
supervisorctl update
supervisorctl restart coconut_calculation

# Set up Nginx configuration
echo "Configuring Nginx..."
NGINX_CONF_PATH="/etc/nginx/sites-available/coconut_calculation.conf"
cp "$PROJECT_BASE_PATH/deploy/nginx_coconut_calculation.conf" "$NGINX_CONF_PATH"
rm -f /etc/nginx/sites-enabled/default
ln -sf "$NGINX_CONF_PATH" /etc/nginx/sites-enabled/coconut_calculation.conf
systemctl restart nginx.service

echo "Deployment complete! :)"
