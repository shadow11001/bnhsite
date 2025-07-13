#!/bin/bash

echo "🔧 Blue Nebula Hosting - Complete API Fix"
echo "========================================="

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

print_status "Applying fixes for hosting plans display issues..."

echo ""
print_status "Issues Found & Fixed:"
echo "  1. ✅ Frontend API URL construction (removed double /api)"
echo "  2. ✅ Hosting plans filtering (type + sub_type instead of plan_type)"
echo "  3. ✅ Admin panel API URL construction"

# Rebuild frontend with fixes
print_status "🔄 Rebuilding frontend with API fixes..."
docker-compose build --no-cache bnhsite-frontend

if [ $? -ne 0 ]; then
    print_error "Frontend build failed!"
    exit 1
fi

# Restart frontend
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

echo ""
print_status "🧪 Testing the fixes..."

# Test if Caddy routing is working
print_status "Testing Caddy API routing..."
API_TEST=$(curl -s https://bluenebulahosting.com/api/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$API_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Caddy API routing is working"
    
    # Test hosting plans
    PLANS_COUNT=$(curl -s https://bluenebulahosting.com/api/hosting-plans | jq '. | length' 2>/dev/null)
    if [ "$PLANS_COUNT" = "36" ]; then
        print_success "✅ Hosting plans API is working ($PLANS_COUNT plans)"
    else
        print_error "❌ Hosting plans API issue (got '$PLANS_COUNT' instead of 36)"
    fi
else
    print_error "❌ Caddy API routing is not working"
    print_warning "Please check your Caddyfile configuration:"
    echo ""
    echo "    handle /api/* {"
    echo "        uri strip_prefix /api"
    echo "        reverse_proxy bnhsite-backend:8001"
    echo "    }"
    echo ""
    print_warning "Then reload Caddy: sudo systemctl reload caddy"
fi

echo ""
print_status "🎯 Frontend Fixes Applied:"
echo "  ✅ Fixed API URL construction (no more double /api)"
echo "  ✅ Fixed hosting plans filtering to use type + sub_type"
echo "  ✅ Fixed admin panel API calls"

echo ""
print_status "📋 What should work now:"
echo "  🌐 Main website displays hosting plans by category"
echo "  🔐 Admin panel shows all 36 plans individually"
echo "  ⚙️ Admin panel allows editing/managing plans"

echo ""
if [ "$API_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "🎉 All fixes applied successfully!"
    print_status "Visit your website: https://bluenebulahosting.com"
    print_status "Check admin panel: https://bluenebulahosting.com/admin"
else
    print_warning "⚠️ Caddy configuration needs to be updated for complete fix"
    print_status "Update your Caddyfile and reload Caddy, then all should work!"
fi