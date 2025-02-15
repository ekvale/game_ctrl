FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user with specific UID/GID
RUN groupadd -r app --gid=999 && \
    useradd -r -g app --uid=999 --create-home app && \
    chown -R app:app /app

# Copy requirements first for better caching
COPY --chown=app:app requirements/ requirements/
RUN pip install -r requirements/production.txt

# Copy project files
COPY --chown=app:app . .

# Set proper permissions (before switching to app user)
RUN mkdir -p /var/www/static /var/www/media \
    && chown -R app:app /var/www/static /var/www/media \
    && chmod -R 755 /var/www/static /var/www/media

# After copying files
COPY --chown=app:app healthcheck.sh /app/
RUN chmod +x /app/healthcheck.sh

# Update healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD ["/app/healthcheck.sh"]

# Switch to non-root user
USER app

# Collect static files
RUN python manage.py collectstatic --noinput

# Add this before the final CMD
RUN echo "Testing settings module..." && \
    DJANGO_SETTINGS_MODULE=game_ctrl.settings.production python -c "import django; django.setup(); from django.conf import settings; print('TEMPLATES:', settings.TEMPLATES)"

# Change the CMD to use gunicorn directly
CMD ["gunicorn", "game_ctrl.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"] 