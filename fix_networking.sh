#!/bin/bash

echo "🔧 Blue Nebula Hosting - Network Fix"
echo "==================================="

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

print_status "Fixing common networking issues..."

echo ""
print_status "🔄 Step 1: Ensuring all containers are running..."
docker-compose up -d

echo ""
print_status "⏳ Step 2: Waiting for containers to start..."
sleep 10

echo ""
print_status "🔍 Step 3: Getting backend container IP..."
BACKEND_IP=$(docker inspect bnhsite-backend --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null | head -1)

if [ ! -z "$BACKEND_IP" ]; then
    print_success "Backend IP: $BACKEND_IP"
else
    print_error "Could not get backend IP"
    exit 1
fi

echo ""
print_status "🧪 Step 4: Testing backend connectivity..."

# Test backend internal
BACKEND_INTERNAL=$(docker exec bnhsite-backend curl -s http://localhost:8001/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$BACKEND_INTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend responding internally"
else
    print_error "❌ Backend not responding internally"
    print_status "Backend logs:"
    docker logs bnhsite-backend --tail 5
    exit 1
fi

# Test backend by IP
IP_TEST=$(curl -s --connect-timeout 5 http://$BACKEND_IP:8001/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$IP_TEST" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend accessible by IP from host"
else
    print_warning "⚠️ Backend not accessible by IP from host"
fi

echo ""
print_status "📋 Caddyfile configurations to try:"
echo ""
echo "Option 1 - Container name (preferred):"
echo "  handle /api/* {"
echo "      uri strip_prefix /api"
echo "      reverse_proxy http://bnhsite-backend:8001"
echo "  }"
echo ""
echo "Option 2 - Direct IP:"
echo "  handle /api/* {"
echo "      uri strip_prefix /api"
echo "      reverse_proxy http://$BACKEND_IP:8001"
echo "  }"
echo ""
echo "Option 3 - No strip prefix (if backend has /api routes):"
echo "  handle /api/* {"
echo "      reverse_proxy http://bnhsite-backend:8001"
echo "  }"

echo ""
print_status "🔧 Network troubleshooting commands:"
echo ""
echo "1. Check if Caddy can reach backend container:"
echo "   # From your host:"
echo "   curl http://$BACKEND_IP:8001/"
echo ""
echo "2. If you have a Caddy container, test from inside it:"
echo "   docker exec <caddy-container> wget -qO- http://bnhsite-backend:8001/"
echo ""
echo "3. Check container networks:"
echo "   docker network ls"
echo "   docker network inspect blue-nebula-network"
echo ""
echo "4. Restart Caddy after config changes:"
echo "   sudo systemctl reload caddy"

echo ""
print_status "🎯 Next Steps:"
echo "1. Update your Caddyfile with one of the configurations above"
echo "2. Reload Caddy: sudo systemctl reload caddy"
echo "3. Test: curl https://bluenebulahosting.com/api/"

echo ""
print_warning "💡 Pro Tip: If container name doesn't work, Caddy might not be on the same Docker network."
print_warning "    You may need to connect Caddy to the 'blue-nebula-network' or use the IP address."

echo ""
if [ "$BACKEND_INTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "🎉 Backend is healthy! The issue is likely Caddy → Backend connectivity."
    print_status "Backend IP for Caddy config: $BACKEND_IP"
else
    print_error "❌ Backend has issues. Fix backend first, then tackle Caddy routing."
fi