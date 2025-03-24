# Use minimal Python image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Use build cache for system dependencies
RUN apk add --no-cache \
    libffi-dev \
    openssl-dev \
    sqlite-dev \
    && rm -rf /var/cache/apk/*  # ✅ Remove package cache after installation

# Cache Python dependencies by copying only requirements.txt first
COPY requirements.txt /app/

# Use Docker's cache for pip dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt  # ✅ Ensures caching efficiency

# Copy the rest of the project files (this step changes frequently)
COPY . /app/

# Run migrations and collect static files (caching for static files)
RUN python manage.py migrate && python manage.py collectstatic --noinput

# Use a cache directory for pip to speed up package installations in future builds
RUN mkdir -p /root/.cache/pip && chmod -R 777 /root/.cache/pip  # ✅ Cache pip installations

# Expose application port
EXPOSE 8000

# Start Gunicorn server with cache options
CMD ["gunicorn", "coconut_app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-"]
