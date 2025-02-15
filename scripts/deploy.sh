#!/bin/bash

# Build the Docker image
docker build -t game-ctrl .

# Tag the image for Digital Ocean registry
docker tag game-ctrl registry.digitalocean.com/game-ctrl/web

# Push to Digital Ocean registry
docker push registry.digitalocean.com/game-ctrl/web

# Apply Kubernetes configs
kubectl apply -f k8s/ 