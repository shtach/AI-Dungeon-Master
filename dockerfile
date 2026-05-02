# Base image: official Python 3.12 on slim Debian
# "slim" = minimal Debian, smaller image size, faster pulls
FROM python:3.12-slim

# Python environment configuration
# PYTHONDONTWRITEBYTECODE: don't create .pyc files (no need in container)
# PYTHONUNBUFFERED: print logs immediately, don't buffer (critical for docker logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container
# All subsequent commands run from /app
WORKDIR /app

# System dependencies
# - postgresql-client: for pg_isready healthchecks and manual psql commands
# After install, clean apt cache to keep image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies FIRST (before copying code)
# This way, Docker caches this layer until requirements files change
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements/development.txt

# Copy the rest of the project
# This is the layer that changes most often, so it's last
COPY . .

# Create static directory to suppress staticfiles.W004 warning
RUN mkdir -p static

# Expose Django's default port
# Note: EXPOSE is documentation only, doesn't actually publish the port
# Port publishing happens in docker-compose.yml
EXPOSE 8000

# Default command (can be overridden by docker-compose.yml)
# 0.0.0.0 instead of 127.0.0.1 — required so traffic from outside the container can reach Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]