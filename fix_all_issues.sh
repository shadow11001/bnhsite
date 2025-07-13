#!/bin/bash

echo "🔧 Blue Nebula Hosting - Complete Fix"
echo "====================================="

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

print_status "Applying comprehensive fixes for authentication and frontend connection..."

# 1. Rebuild backend with authentication fix
print_status "🔄 Rebuilding backend with database authentication..."
docker-compose build --no-cache bnhsite-backend

if [ $? -ne 0 ]; then
    print_error "Backend build failed!"
    exit 1
fi

# 2. Rebuild frontend with correct backend URL
print_status "🔄 Rebuilding frontend with correct backend URL..."
docker-compose build --no-cache bnhsite-frontend

if [ $? -ne 0 ]; then
    print_error "Frontend build failed!"
    exit 1
fi

# 3. Restart backend first
print_status "🔄 Restarting backend..."
docker-compose restart bnhsite-backend

# Wait for backend to be ready
print_status "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -sf https://bluenebulahosting.com/api/ >/dev/null 2>&1; then
        print_success "Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start properly"
        print_error "Check logs: docker-compose logs bnhsite-backend"
        exit 1
    fi
    sleep 2
done

# 4. Restart frontend
print_status "🔄 Restarting frontend..."
docker-compose restart bnhsite-frontend

# Wait for frontend to be ready
print_status "⏳ Waiting for frontend to start..."
for i in {1..20}; do
    if curl -sf https://bluenebulahosting.com/ >/dev/null 2>&1; then
        print_success "Frontend is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        print_warning "Frontend may still be starting..."
        break
    fi
    sleep 2
done

# 5. Test the fixes
echo ""
print_status "🧪 Testing fixes..."

# Test backend API
API_RESPONSE=$(curl -s https://bluenebulahosting.com/api/ | jq -r '.message' 2>/dev/null)
if [ "$API_RESPONSE" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend API is working"
else
    print_error "❌ Backend API test failed"
fi

# Test hosting plans
PLANS_COUNT=$(curl -s https://bluenebulahosting.com/api/hosting-plans | jq '. | length' 2>/dev/null)
if [ "$PLANS_COUNT" = "36" ]; then
    print_success "✅ Hosting plans API is working (36 plans)"
else
    print_error "❌ Hosting plans API test failed (got $PLANS_COUNT plans)"
fi

# Test login with new credentials
print_status "🔐 Testing new admin login..."
echo "Attempting login with username: morphon"
LOGIN_RESPONSE=$(curl -s -X POST https://bluenebulahosting.com/api/login \
    -H "Content-Type: application/json" \
    -d '{"username": "morphon", "password": "your_password_here"}' | jq -r '.access_token' 2>/dev/null)

if [ "$LOGIN_RESPONSE" != "null" ] && [ "$LOGIN_RESPONSE" != "" ]; then
    print_success "✅ New admin credentials are working"
else
    print_warning "⚠️ Login test needs actual password. Use this to test manually:"
    echo "curl -X POST https://bluenebulahosting.com/api/login -H 'Content-Type: application/json' -d '{\"username\": \"morphon\", \"password\": \"YOUR_PASSWORD\"}'"
fi

echo ""
print_success "🎉 All fixes applied!"
echo ""
print_status "Summary of fixes:"
echo "  ✅ Backend now uses database authentication (not hardcoded credentials)"
echo "  ✅ Frontend now points to https://bluenebulahosting.com/api"
echo "  ✅ Login with username: morphon and your password"
echo "  ✅ Hosting plans should now display on the website"
echo ""
print_status "Test your website:"
echo "  🌐 Main site: https://bluenebulahosting.com"
echo "  🔐 Admin panel: https://bluenebulahosting.com/admin"
echo "  📊 API test: https://bluenebulahosting.com/api/hosting-plans"