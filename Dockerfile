# Use a minimal Python image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (SQLite for Django)
RUN apk add --no-cache \
    libffi-dev \
    openssl-dev \
    sqlite-dev \
    && rm -rf /var/cache/apk/*  # ✅ Remove package cache after installation

# Copy only requirements first for caching dependencies
COPY requirements.txt /app/

# Use Docker's cache for pip dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt  # ✅ Ensures caching efficiency

# Copy the entire project after dependencies are installed
COPY . /app/

# Ensure static files directory exists
RUN mkdir -p /app/staticfiles

# Run migrations and collect static files
RUN python manage.py migrate && python manage.py collectstatic --noinput

# Expose application port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "coconut_app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
