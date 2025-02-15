#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Start Docker
systemctl start docker
systemctl enable docker

# Clone repository (you'll need to set up deploy keys)
git clone https://github.com/your-username/game_ctrl.git /opt/game_ctrl

# Create necessary directories
mkdir -p /var/log/django
mkdir -p /var/www/static
mkdir -p /var/www/media

# Set up environment file
cp /opt/game_ctrl/.env.prod.template /opt/game_ctrl/.env.prod

# Start services
cd /opt/game_ctrl
docker-compose -f docker-compose.prod.yml up -d 