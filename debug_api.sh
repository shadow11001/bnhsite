#!/bin/bash

echo "🔍 Blue Nebula Hosting - API Debugging"
echo "======================================"

echo "🧪 Testing API endpoints..."

echo -e "\n1. Testing direct backend connection:"
echo "   docker exec bnhsite-backend curl -s http://localhost:8001/"
echo "   Response:"
curl -s http://localhost:8001/ 2>/dev/null || echo "   ❌ Could not connect to backend directly"

echo -e "\n2. Testing through Caddy - Root API:"
echo "   curl -s https://bluenebulahosting.com/api/"
echo "   Response:"
RESPONSE=$(curl -s https://bluenebulahosting.com/api/)
echo "   $RESPONSE"

if [[ "$RESPONSE" == *"Not Found"* ]]; then
    echo "   ❌ API endpoint not found through Caddy"
else
    echo "   ✅ API endpoint working"
fi

echo -e "\n3. Testing hosting plans endpoint:"
echo "   curl -s https://bluenebulahosting.com/api/hosting-plans"
echo "   Response:"
PLANS_RESPONSE=$(curl -s https://bluenebulahosting.com/api/hosting-plans)
echo "   $PLANS_RESPONSE" | head -100

if [[ "$PLANS_RESPONSE" == *"Not Found"* ]]; then
    echo "   ❌ Hosting plans endpoint not found"
else
    echo "   ✅ Hosting plans endpoint working"
fi

echo -e "\n4. Testing if Caddy configuration was applied:"
echo "   Checking recent Caddy reload..."

echo -e "\n🔧 Suggested fixes:"
echo "1. Ensure your Caddyfile has been updated with:"
echo "   handle /api/* {"
echo "       uri strip_prefix /api"
echo "       reverse_proxy bnhsite-backend:8001"
echo "   }"
echo ""
echo "2. Reload Caddy configuration:"
echo "   sudo systemctl reload caddy"
echo "   # or"
echo "   caddy reload"
echo ""
echo "3. Check Caddy logs for errors:"
echo "   sudo journalctl -u caddy -f"

echo -e "\n📋 Current backend container status:"
echo "   Container name: bnhsite-backend"
echo "   Expected internal URL: bnhsite-backend:8001"
echo "   Expected external URL: https://bluenebulahosting.com/api/"