# Use a minimal Python image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for Django, SQLite, Pillow, etc.
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    python3-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    sqlite-dev \
    gcc \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements file first to cache layer
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app/

# Ensure static & media directories exist
RUN mkdir -p /app/staticfiles /app/media

# Fix manage.py execution permission
RUN chmod +x manage.py

# Expose port 8000
EXPOSE 8000

# Command to run the app with Gunicorn
CMD ["gunicorn", "--chdir", "/app", "coconut_app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--timeout=120"]
