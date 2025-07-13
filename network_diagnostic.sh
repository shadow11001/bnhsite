#!/bin/bash

echo "🔍 Blue Nebula Hosting - Network & Connectivity Diagnostic"
echo "========================================================"

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

echo ""
print_status "🔍 Step 1: Container Status & Networks"
echo "Container Status:"
docker ps --filter "name=bnhsite" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Container Networks:"
for container in bnhsite-mongodb bnhsite-backend bnhsite-frontend; do
    if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
        networks=$(docker inspect $container --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}')
        echo "$container: $networks"
    else
        echo "$container: NOT RUNNING"
    fi
done

echo ""
print_status "🔍 Step 2: Backend Container Connectivity"
if docker ps --filter "name=bnhsite-backend" --format "{{.Names}}" | grep -q "bnhsite-backend"; then
    echo "Testing backend internal API:"
    BACKEND_INTERNAL=$(docker exec bnhsite-backend curl -s http://localhost:8001/ 2>/dev/null || echo "FAILED")
    echo "Response: $BACKEND_INTERNAL"
    
    echo ""
    echo "Backend container IP:"
    docker inspect bnhsite-backend --format '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'
    
    echo ""
    echo "Backend listening ports:"
    docker exec bnhsite-backend netstat -tlnp 2>/dev/null | grep :8001 || echo "Port 8001 not listening"
else
    print_error "Backend container not running!"
fi

echo ""
print_status "🔍 Step 3: Caddy to Backend Connectivity"
echo "Caddy process check:"
if pgrep caddy > /dev/null; then
    print_success "Caddy is running"
    
    echo ""
    echo "Testing if Caddy can reach backend container:"
    
    # Method 1: Test with container name
    echo "Test 1 - Container name resolution:"
    if command -v docker >/dev/null 2>&1; then
        # Test from a temporary container on the same network
        BACKEND_IP=$(docker inspect bnhsite-backend --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null | head -1)
        if [ ! -z "$BACKEND_IP" ]; then
            echo "Backend IP: $BACKEND_IP"
            
            # Test direct IP connection
            echo "Testing direct IP connection:"
            if command -v curl >/dev/null 2>&1; then
                curl -s --connect-timeout 5 http://$BACKEND_IP:8001/ || echo "Direct IP connection failed"
            fi
            
            # Test container name resolution from host
            echo "Testing container name resolution:"
            if docker run --rm --network=blue-nebula-network alpine:latest sh -c "wget -qO- --timeout=5 http://bnhsite-backend:8001/ || echo 'Container name resolution failed'" 2>/dev/null; then
                print_success "Container name resolution works"
            else
                print_error "Container name resolution failed"
            fi
        else
            print_error "Could not get backend IP"
        fi
    fi
else
    print_error "Caddy is not running!"
fi

echo ""
print_status "🔍 Step 4: External API Tests"
echo "Testing external API endpoints:"

# Test root API
echo ""
echo "Test 1: https://bluenebulahosting.com/api/"
API_ROOT=$(curl -s --connect-timeout 10 https://bluenebulahosting.com/api/ 2>/dev/null || echo "TIMEOUT/FAILED")
echo "Response: $API_ROOT"

# Test without /api prefix (to see what Caddy is doing)
echo ""
echo "Test 2: https://bluenebulahosting.com/ (frontend)"
FRONTEND_TEST=$(curl -s --connect-timeout 10 -I https://bluenebulahosting.com/ 2>/dev/null | head -1 || echo "TIMEOUT/FAILED")
echo "Response: $FRONTEND_TEST"

# Test direct backend port (if exposed)
echo ""
echo "Test 3: https://bluenebulahosting.com:8001/ (direct backend)"
DIRECT_BACKEND=$(curl -s --connect-timeout 10 https://bluenebulahosting.com:8001/ 2>/dev/null || echo "TIMEOUT/FAILED")
echo "Response: $DIRECT_BACKEND"

echo ""
print_status "🔍 Step 5: Caddy Configuration Check"
echo "Current Caddyfile excerpt (if readable):"
if [ -f "/etc/caddy/Caddyfile" ]; then
    grep -A 10 -B 2 "handle /api" /etc/caddy/Caddyfile 2>/dev/null || echo "Could not read Caddyfile or no /api handler found"
else
    echo "Caddyfile not found at /etc/caddy/Caddyfile"
fi

echo ""
print_status "📋 Diagnostic Summary & Recommendations"

# Check backend status
if docker ps --filter "name=bnhsite-backend" --format "{{.Names}}" | grep -q "bnhsite-backend"; then
    if [[ "$BACKEND_INTERNAL" == *"Blue Nebula Hosting API"* ]]; then
        print_success "✅ Backend: Running and responding internally"
    else
        print_error "❌ Backend: Running but not responding on :8001"
        echo "   → Check backend logs: docker logs bnhsite-backend"
    fi
else
    print_error "❌ Backend: Container not running"
    echo "   → Start backend: docker-compose up -d bnhsite-backend"
fi

# Check external API
if [[ "$API_ROOT" == *"Blue Nebula Hosting API"* ]]; then
    print_success "✅ External API: Working through Caddy"
elif [[ "$API_ROOT" == *"TIMEOUT"* ]] || [[ "$API_ROOT" == *"FAILED"* ]]; then
    print_error "❌ External API: Caddy cannot reach backend"
    echo "   → Possible causes:"
    echo "     1. Backend container not on same network as Caddy"
    echo "     2. Caddy configuration incorrect"
    echo "     3. Backend container not accessible by name 'bnhsite-backend'"
else
    print_warning "⚠️ External API: Unexpected response"
    echo "   → Response: $API_ROOT"
fi

echo ""
print_status "🔧 Quick Fixes to Try:"
echo ""
echo "1. Ensure backend is running and healthy:"
echo "   docker-compose up -d bnhsite-backend"
echo "   docker logs bnhsite-backend"
echo ""
echo "2. Check if Caddy can access the backend network:"
echo "   # Add Caddy to the blue-nebula-network if not already"
echo ""
echo "3. Alternative Caddyfile configuration (try this):"
echo "   handle /api/* {"
echo "       uri strip_prefix /api"
echo "       reverse_proxy http://bnhsite-backend:8001"  # Note: explicit http://"
echo "   }"
echo ""
echo "4. Or try with backend IP instead of container name:"
echo "   handle /api/* {"
echo "       uri strip_prefix /api"
echo "       reverse_proxy http://$BACKEND_IP:8001"
echo "   }"
echo ""
echo "5. Check Caddy can resolve container name:"
echo "   docker exec <caddy-container> nslookup bnhsite-backend"