#!/bin/bash

echo "🔐 Blue Nebula Hosting - Change Admin Credentials"
echo "==============================================="

# Check if backend container is running
if docker ps | grep -q "bnhsite-backend"; then
    echo "✅ Backend container is running"
    echo "🔄 Running credential change script..."
    docker exec -it bnhsite-backend python3 change_admin_credentials.py
else
    echo "❌ Backend container 'bnhsite-backend' is not running"
    echo "Please start it first with: docker-compose up -d bnhsite-backend"
    exit 1
fi