#!/usr/bin/env bash
set -euo pipefail

echo "Installing Docker Engine and Docker Compose v2 on Ubuntu..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2

echo "Enabling Docker service..."
sudo systemctl enable --now docker

echo "Adding current user to docker group..."
sudo usermod -aG docker "$USER"

cat <<'MSG'

Docker installation finished.

Important:
1. Log out and log back in, or run:
   newgrp docker
2. Verify:
   docker --version
   docker compose version
   docker run --rm hello-world

MSG
