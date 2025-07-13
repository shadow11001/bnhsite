#!/bin/bash

echo "🔧 Blue Nebula Hosting - Fix API Routing"
echo "========================================"

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

print_status "Fixing API routing architecture..."

echo ""
print_status "🔍 Root Cause Found:"
echo "  - Backend had APIRouter(prefix='/api') which added /api to all routes"
echo "  - Caddy forwards /api/* to backend, creating /api/api double prefix"
echo "  - Solution: Remove /api prefix from backend, let Caddy handle routing"

echo ""
print_status "✅ Fixes Applied:"
echo "  1. Removed APIRouter prefix='/api' from backend"
echo "  2. Updated frontend API calls"
echo "  3. Caddy can now use uri strip_prefix /api"

echo ""
print_status "🔄 Rebuilding and restarting services..."

# Rebuild backend
print_status "Building backend..."
docker-compose build --no-cache bnhsite-backend

if [ $? -ne 0 ]; then
    print_error "Backend build failed!"
    exit 1
fi

# Rebuild frontend
print_status "Building frontend..."
docker-compose build --no-cache bnhsite-frontend

if [ $? -ne 0 ]; then
    print_error "Frontend build failed!"
    exit 1
fi

# Restart backend first
print_status "Restarting backend..."
docker-compose restart bnhsite-backend

# Wait for backend
print_status "Waiting for backend..."
for i in {1..30}; do
    if docker exec bnhsite-backend curl -sf http://localhost:8001/ >/dev/null 2>&1; then
        print_success "Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        exit 1
    fi
    sleep 2
done

# Restart frontend
print_status "Restarting frontend..."
docker-compose restart bnhsite-frontend

# Wait for frontend
print_status "Waiting for frontend..."
sleep 10

echo ""
print_status "🧪 Testing the new routing..."

# Test direct backend call
print_status "Testing backend directly..."
BACKEND_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/ | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend responding on root route"
else
    print_error "❌ Backend not responding correctly"
fi

# Test plans endpoint directly
BACKEND_PLANS=$(docker exec bnhsite-backend curl -s http://localhost:8001/hosting-plans | jq '. | length' 2>/dev/null)
if [ "$BACKEND_PLANS" = "36" ]; then
    print_success "✅ Backend hosting-plans endpoint working ($BACKEND_PLANS plans)"
else
    print_error "❌ Backend hosting-plans endpoint failed (got: $BACKEND_PLANS)"
fi

echo ""
print_status "📋 Caddy Configuration:"
echo "  Your Caddyfile should now work with:"
echo ""
echo "    handle /api/* {"
echo "        uri strip_prefix /api"
echo "        reverse_proxy bnhsite-backend:8001"
echo "    }"
echo ""
echo "  This will:"
echo "    1. Receive: /api/hosting-plans"
echo "    2. Strip: /hosting-plans"
echo "    3. Forward: http://bnhsite-backend:8001/hosting-plans"
echo "    4. Backend serves: /hosting-plans (no prefix needed)"

echo ""
print_warning "⚠️ Important: Reload your Caddy configuration:"
echo "  sudo systemctl reload caddy"
echo "  # or"
echo "  caddy reload"

echo ""
print_status "🎯 After Caddy reload, test:"
echo "  curl https://bluenebulahosting.com/api/"
echo "  curl https://bluenebulahosting.com/api/hosting-plans"
echo ""
print_status "🌐 Website: https://bluenebulahosting.com"
print_status "🔐 Admin: https://bluenebulahosting.com/admin"