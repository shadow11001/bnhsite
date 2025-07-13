#!/bin/bash

echo "🔍 Blue Nebula Hosting - API Diagnostic & Fix"
echo "============================================="

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
print_status "🔍 Step 1: Checking container status..."
docker-compose ps

echo ""
print_status "🔍 Step 2: Testing direct backend connection..."
BACKEND_DIRECT=$(docker exec bnhsite-backend curl -s http://localhost:8001/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$BACKEND_DIRECT" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend is responding internally"
else
    print_error "❌ Backend not responding internally"
    print_status "Checking backend logs:"
    docker logs bnhsite-backend --tail 10
fi

echo ""
print_status "🔍 Step 3: Testing MongoDB connection from backend..."
MONGO_TEST=$(docker exec bnhsite-backend python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def test():
    try:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@bnhsite-mongodb:27017/blue_nebula_hosting?authSource=admin')
        print(f'Using MongoDB URL: {mongo_url}')
        client = AsyncIOMotorClient(mongo_url)
        await client.admin.command('ping')
        print('✅ MongoDB connection successful')
        
        # Check database collections
        db = client['blue_nebula_hosting']
        collections = await db.list_collection_names()
        print(f'Collections found: {collections}')
        
        # Check hosting plans count
        plans_count = await db.hosting_plans.count_documents({})
        print(f'Hosting plans in database: {plans_count}')
        
        client.close()
        return True
    except Exception as e:
        print(f'❌ MongoDB connection failed: {e}')
        return False

asyncio.run(test())
" 2>&1)

echo "$MONGO_TEST"

echo ""
print_status "🔍 Step 4: Testing external API access through Caddy..."
API_EXTERNAL=$(curl -s https://bluenebulahosting.com/api/ 2>/dev/null | grep -o "Blue Nebula Hosting API" || echo "FAILED")

if [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "✅ API accessible through Caddy"
else
    print_error "❌ API not accessible through Caddy"
    print_warning "This suggests a Caddy configuration issue"
fi

echo ""
print_status "🔍 Step 5: Testing hosting plans endpoint..."
if [ "$BACKEND_DIRECT" = "Blue Nebula Hosting API" ]; then
    PLANS_DIRECT=$(docker exec bnhsite-backend curl -s http://localhost:8001/hosting-plans | jq '. | length' 2>/dev/null || echo "FAILED")
    print_status "Direct backend plans count: $PLANS_DIRECT"
fi

if [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    PLANS_EXTERNAL=$(curl -s https://bluenebulahosting.com/api/hosting-plans | jq '. | length' 2>/dev/null || echo "FAILED")
    print_status "External API plans count: $PLANS_EXTERNAL"
fi

echo ""
print_status "📋 Diagnostic Summary:"

# Backend check
if [ "$BACKEND_DIRECT" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Backend: Working"
else
    print_error "❌ Backend: Not responding"
fi

# MongoDB check
if [[ "$MONGO_TEST" == *"MongoDB connection successful"* ]]; then
    print_success "✅ MongoDB: Connected"
    
    if [[ "$MONGO_TEST" == *"Hosting plans in database: 0"* ]]; then
        print_warning "⚠️ Database: Empty (needs initialization)"
        DB_NEEDS_INIT=true
    else
        print_success "✅ Database: Has data"
        DB_NEEDS_INIT=false
    fi
else
    print_error "❌ MongoDB: Connection failed"
    DB_NEEDS_INIT=true
fi

# API access check
if [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ]; then
    print_success "✅ Caddy: Routing working"
else
    print_error "❌ Caddy: Routing not working"
fi

echo ""
print_status "🔧 Recommended Actions:"

# Fix actions
if [ "$BACKEND_DIRECT" != "Blue Nebula Hosting API" ]; then
    echo "1. Restart backend: docker-compose restart bnhsite-backend"
fi

if [[ "$MONGO_TEST" != *"MongoDB connection successful"* ]]; then
    echo "2. Check MongoDB: docker-compose logs bnhsite-mongodb"
    echo "3. Verify MongoDB environment variables in backend"
fi

if [ "$DB_NEEDS_INIT" = true ]; then
    echo "4. Initialize database: docker exec bnhsite-backend python3 init_database.py"
fi

if [ "$API_EXTERNAL" != "Blue Nebula Hosting API" ]; then
    echo "5. Check Caddy configuration and reload: sudo systemctl reload caddy"
    echo "6. Verify Caddyfile has: uri strip_prefix /api"
fi

echo ""
print_status "🚀 Quick Fix Commands:"
echo "# Restart services"
echo "docker-compose restart bnhsite-backend bnhsite-frontend"
echo ""
echo "# Initialize database"
echo "docker exec bnhsite-backend python3 init_database.py"
echo ""
echo "# Test API"
echo "curl https://bluenebulahosting.com/api/"
echo "curl https://bluenebulahosting.com/api/hosting-plans"

echo ""
if [ "$BACKEND_DIRECT" = "Blue Nebula Hosting API" ] && [ "$API_EXTERNAL" = "Blue Nebula Hosting API" ] && [ "$DB_NEEDS_INIT" = false ]; then
    print_success "🎉 Everything looks good! API should be working."
else
    print_warning "⚠️ Issues found. Follow the recommended actions above."
fi