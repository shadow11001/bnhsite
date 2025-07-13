#!/bin/bash

echo "🔧 Removing problematic hardcoded hosting plans from backend"

# Create a backup
cp /app/backend/server.py /app/backend/server.py.backup

# Find where the init-data function starts and ends
echo "Finding problematic function..."

# Remove everything from the init-data function to its end
sed -i '/^# COMMENTED OUT - Using database initialization script instead/,/^    except Exception as e:/c\
# Hardcoded hosting plans removed - using database initialization script instead' /app/backend/server.py

echo "✅ Removed hardcoded hosting plans"
echo "🔄 Rebuilding and restarting backend..."

cd /app
docker-compose build blue-nebula-backend
docker-compose restart blue-nebula-backend

echo "⏳ Waiting for backend to start..."
sleep 10

echo "🧪 Testing API..."
curl -s https://bluenebulahosting.com/api/hosting-plans | head -20

echo "✅ Backend fixed and restarted!"