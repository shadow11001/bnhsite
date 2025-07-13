#!/bin/bash

echo "🔧 Blue Nebula Hosting - Quick API Fix"
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

print_status "Applying common fixes for fresh environment..."

echo ""
print_status "🔄 Step 1: Restarting services..."
docker-compose restart bnhsite-backend bnhsite-frontend

echo ""
print_status "⏳ Step 2: Waiting for services to start..."
sleep 10

echo ""
print_status "🔄 Step 3: Initializing fresh database..."
docker exec bnhsite-backend python3 init_database.py

echo ""
print_status "🧪 Step 4: Testing API..."

# Test backend directly
BACKEND_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/ | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend API working"
    
    # Test plans
    PLANS_COUNT=$(docker exec bnhsite-backend curl -s http://localhost:8001/hosting-plans | jq '. | length' 2>/dev/null)
    print_status "Hosting plans in database: $PLANS_COUNT"
    
    if [ "$PLANS_COUNT" = "36" ]; then
        print_success "✅ Database initialized with all 36 plans"
    else
        print_warning "⚠️ Expected 36 plans, got $PLANS_COUNT"
    fi
else
    print_error "❌ Backend API not working"
    print_status "Backend logs:"
    docker logs bnhsite-backend --tail 5
fi

echo ""
print_status "🌐 Step 5: Testing external access..."
API_EXTERNAL=$(curl -s https://bluenebulahosting.com/api/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "✅ External API access working"
else
    print_error "❌ External API access not working"
    print_warning "Check your Caddyfile configuration:"
    echo ""
    echo "    handle /api/* {"
    echo "        uri strip_prefix /api"
    echo "        reverse_proxy bnhsite-backend:8001"
    echo "    }"
    echo ""
    print_warning "Then reload Caddy: sudo systemctl reload caddy"
fi

echo ""
print_status "📋 Current Status:"
if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend: Working"
else
    print_error "❌ Backend: Not working"
fi

if [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "✅ External API: Working"
else
    print_error "❌ External API: Caddy configuration needed"
fi

if [ "$PLANS_COUNT" = "36" ]; then
    print_success "✅ Database: Initialized with hosting plans"
else
    print_warning "⚠️ Database: May need reinitialization"
fi

echo ""
print_status "🎯 Test URLs:"
echo "  Backend direct: docker exec bnhsite-backend curl http://localhost:8001/"
echo "  External API: curl https://bluenebulahosting.com/api/"
echo "  Hosting plans: curl https://bluenebulahosting.com/api/hosting-plans"
echo "  Website: https://bluenebulahosting.com"

echo ""
if [ "$BACKEND_TEST" = "Blue Nebula Hosting API" ] && [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "🎉 API is working! Your site should display hosting plans."
else
    print_warning "⚠️ Some issues remain. Use ./diagnose_api.sh for detailed analysis."
fi