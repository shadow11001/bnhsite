#!/bin/bash

echo "🔧 Fixing Backend API and Restarting Services"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "backend/server.py" ]; then
    echo "❌ Please run this script from your Blue Nebula Hosting directory"
    exit 1
fi

# Rebuild and restart backend
echo "🔄 Rebuilding backend with fixes..."
docker-compose build blue-nebula-backend

echo "🔄 Restarting backend..."
docker-compose restart blue-nebula-backend

echo "⏳ Waiting for backend to start..."
sleep 10

echo "🧪 Testing API endpoints..."
echo "Testing root API:"
curl -s https://bluenebulahosting.com/api/ | jq

echo -e "\nTesting hosting plans API:"
curl -s https://bluenebulahosting.com/api/hosting-plans | jq '. | length'

echo -e "\n✅ Backend fixes applied and restarted!"
echo "Your hosting plans should now display on the website."