FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

ENV DJANGO_SETTINGS_MODULE=game_ctrl.settings.production


# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create app user first
RUN groupadd -r app && useradd -r -g app app

# Create directories and set permissions
RUN mkdir -p /var/www/static /var/www/media \
    && chown -R app:app /var/www/static /var/www/media \
    && chmod -R 755 /var/www/static /var/www/media

# Copy requirements first
COPY --chown=app:app requirements/ requirements/
RUN pip install -r requirements/production.txt

# Copy env file and set permissions
COPY --chown=app:app .env.prod .env.prod
RUN chmod 644 .env.prod

# Copy the rest of the application code
COPY --chown=app:app . .

# Copy and set up healthcheck
COPY --chown=app:app healthcheck.sh /app/
RUN chmod +x /app/healthcheck.sh

# Update healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD ["/app/healthcheck.sh"]

# Switch to app user
USER app

# Collect static files
RUN DJANGO_SETTINGS_MODULE=game_ctrl.settings.production python manage.py collectstatic --noinput

# Test settings
RUN echo "Testing settings module..." && \
    DJANGO_SETTINGS_MODULE=game_ctrl.settings.production python -c "import django; django.setup(); from django.conf import settings; print('TEMPLATES:', settings.TEMPLATES)"

CMD ["gunicorn", "game_ctrl.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"] 
