# Use a minimal Python image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (for SQLite & cryptography)
RUN apk add --no-cache \
    libffi-dev \
    openssl-dev \
    sqlite-dev \
    gcc \
    musl-dev \
    python3-dev \
    && rm -rf /var/cache/apk/*  # ✅ Remove package cache after installation

# Copy only requirements first for caching dependencies
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt  # ✅ Ensures caching efficiency

# Copy the entire project after dependencies are installed
COPY . /app/

# Ensure static & media directories exist
RUN mkdir -p /app/staticfiles /app/media

# Fix execution permissions for manage.py
RUN chmod +x manage.py

# Expose application port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--chdir", "/app", "coconut_app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
