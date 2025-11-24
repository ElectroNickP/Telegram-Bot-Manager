#!/bin/bash
set -e

echo "🚀 Starting update process..."

# Pull latest changes
echo "📥 Pulling git changes..."
git pull

# Build containers
echo "🏗️ Building containers..."
docker-compose build

# Run migrations
echo "🔄 Running database migrations..."
docker-compose run --rm web alembic upgrade head

# Restart services
echo "♻️ Restarting services..."
docker-compose up -d

echo "✅ Update complete!"
