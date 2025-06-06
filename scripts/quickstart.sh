#!/usr/bin/env bash
set -e

# Ensure script is executed from project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Build and start containers
docker-compose up --build -d

# Display URLs
echo "Services are starting..."
echo "API: http://localhost"
echo "Frontend: http://localhost:3000"
