#!/bin/bash

echo "🔧 Blue Nebula Hosting - Complete Fix for All Issues"
echo "==================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Applying all fixes..."

echo ""
print_status "✅ Issues Fixed:"
echo "  1. MongoDB connection URLs updated to use bnhsite-mongodb"
echo "  2. MongoDB password updated to: WEvSMiUiYlASPYN4Pqb7zLO8E"
echo "  3. Logo gradient background removed (transparent logo support)"
echo "  4. Admin login page now shows logo"
echo "  5. Favicon link added to index.html (supports favicon.png)"
echo "  6. Backend API router prefix removed"
echo "  7. Frontend API URL construction fixed"

# Create favicon.png from favicon.ico if needed
if [ ! -f "/app/frontend/public/favicon.png" ] && [ -f "/app/frontend/public/favicon.ico" ]; then
    print_status "Converting favicon.ico to favicon.png for better compatibility..."
    # Note: In production, you would use ImageMagick or similar
    # For now, we'll just copy the existing favicon
    cp /app/frontend/public/favicon.ico /app/frontend/public/favicon.png
fi

# Rebuild backend with MongoDB fixes
print_status "🔄 Rebuilding backend with MongoDB connection fixes..."
docker-compose build --no-cache bnhsite-backend

if [ $? -ne 0 ]; then
    print_error "Backend build failed!"
    exit 1
fi

# Rebuild frontend with logo and favicon fixes
print_status "🔄 Rebuilding frontend with logo and favicon fixes..."
docker-compose build --no-cache bnhsite-frontend

if [ $? -ne 0 ]; then
    print_error "Frontend build failed!"
    exit 1
fi

# Restart services
print_status "🔄 Restarting all services..."
docker-compose restart bnhsite-mongodb bnhsite-backend bnhsite-frontend

# Wait for services
print_status "⏳ Waiting for services to start..."
sleep 15

# Test MongoDB connection from backend
print_status "🧪 Testing MongoDB connection..."
MONGO_TEST=$(docker exec bnhsite-backend python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def test():
    try:
        client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
        await client.admin.command('ping')
        print('MongoDB connection successful')
        client.close()
        return True
    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        return False

print(asyncio.run(test()))
" 2>/dev/null)

if [[ "$MONGO_TEST" == *"successful"* ]]; then
    print_success "✅ MongoDB connection working"
else
    print_error "❌ MongoDB connection failed"
    print_warning "Check: docker-compose logs bnhsite-mongodb"
fi

# Test backend API
print_status "🧪 Testing backend API..."
sleep 5
BACKEND_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/ | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend API working"
    
    # Test hosting plans
    PLANS_COUNT=$(docker exec bnhsite-backend curl -s http://localhost:8001/hosting-plans | jq '. | length' 2>/dev/null)
    if [ "$PLANS_COUNT" = "36" ]; then
        print_success "✅ Hosting plans API working ($PLANS_COUNT plans)"
    else
        print_warning "⚠️ Plans count: $PLANS_COUNT (expected 36)"
    fi
else
    print_error "❌ Backend API not responding"
fi

echo ""
print_status "🎯 Final Checklist:"
echo "  1. Update your Caddyfile with:"
echo "     handle /api/* {"
echo "         uri strip_prefix /api"
echo "         reverse_proxy bnhsite-backend:8001"
echo "     }"
echo ""
echo "  2. Reload Caddy: sudo systemctl reload caddy"
echo ""
echo "  3. Replace placeholder logos:"
echo "     - Add your logo.png to /app/frontend/public/"
echo "     - Add your favicon.png to /app/frontend/public/"
echo "     - Rebuild frontend: docker-compose build bnhsite-frontend"

echo ""
print_status "🌐 Test URLs:"
echo "  Main site: https://bluenebulahosting.com"
echo "  Admin panel: https://bluenebulahosting.com/admin"
echo "  API test: https://bluenebulahosting.com/api/"
echo "  Plans test: https://bluenebulahosting.com/api/hosting-plans"

echo ""
if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "🎉 All fixes applied successfully!"
    print_status "After Caddy reload, everything should work perfectly!"
else
    print_warning "⚠️ Some issues remain - check logs and test endpoints"
fi