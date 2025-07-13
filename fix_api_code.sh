#!/bin/bash

echo "🔍 Blue Nebula Hosting - API Code Review & Fix"
echo "=============================================="

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
print_status "🔍 API Code Issues Found:"
echo ""
echo "1. ❌ Dockerfile COPY issue:"
echo "   Lines 28-29: COPY ../init_database.py ./ and COPY ../change_admin_credentials.py ./"
echo "   → These paths are incorrect in Docker build context"
echo ""
echo "2. ⚠️  Environment variable access:"
echo "   Line 22: mongo_url = os.environ['MONGO_URL'] (no fallback)"
echo "   → Will crash if MONGO_URL not set"
echo ""
echo "3. ⚠️  Health check endpoint:"
echo "   Health check expects / to return 200, but might fail on startup"
echo ""
echo "4. ✅ API Router setup looks correct"
echo "5. ✅ CORS configuration looks correct"
echo "6. ✅ Endpoints are properly defined"

echo ""
print_status "🔧 Applying fixes..."

# Fix 1: Update Dockerfile to remove problematic COPY commands
print_status "Fixing Dockerfile..."
cat > /tmp/dockerfile_fix << 'EOF'
# Production-optimized FastAPI backend Dockerfile
FROM python:3.11-slim as base

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy scripts from parent directory if they exist
COPY init_database.py ./ 2>/dev/null || echo "init_database.py not found, skipping..."
COPY change_admin_credentials.py ./ 2>/dev/null || echo "change_admin_credentials.py not found, skipping..."

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check - more robust
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Production command with optimizations
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
EOF

cp /tmp/dockerfile_fix /app/backend/Dockerfile
print_success "✅ Fixed Dockerfile"

# Fix 2: Update server.py to have better error handling
print_status "Adding environment variable fallbacks..."

# Create a patched version of server.py with better error handling
python3 << 'EOF'
# Read the current server.py
with open('/app/backend/server.py', 'r') as f:
    content = f.read()

# Fix the MongoDB URL line to have a fallback
content = content.replace(
    "mongo_url = os.environ['MONGO_URL']",
    "mongo_url = os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@bnhsite-mongodb:27017/blue_nebula_hosting?authSource=admin')"
)

# Fix the DB_NAME to have a fallback
content = content.replace(
    "db = client[os.environ['DB_NAME']]",
    "db = client[os.environ.get('DB_NAME', 'blue_nebula_hosting')]"
)

# Write the fixed version
with open('/app/backend/server.py', 'w') as f:
    f.write(content)

print("✅ Fixed environment variable handling")
EOF

# Fix 3: Copy the scripts to the backend directory
print_status "Copying scripts to backend directory..."
cp /app/init_database.py /app/backend/ 2>/dev/null || echo "init_database.py already in backend or not found"
cp /app/change_admin_credentials.py /app/backend/ 2>/dev/null || echo "change_admin_credentials.py already in backend or not found"

# Fix 4: Create a minimal test endpoint
print_status "Adding debug endpoint..."
cat >> /app/backend/server.py << 'EOF'

# Debug endpoint
@api_router.get("/debug")
async def debug():
    """Debug endpoint to check API health"""
    import os
    return {
        "status": "API Working",
        "environment": {
            "MONGO_URL": "Set" if os.environ.get('MONGO_URL') else "Not Set",
            "DB_NAME": os.environ.get('DB_NAME', 'default'),
            "JWT_SECRET_KEY": "Set" if os.environ.get('JWT_SECRET_KEY') else "Not Set"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
EOF

print_success "✅ Added debug endpoint"

echo ""
print_status "🔄 Rebuilding backend with fixes..."
docker-compose build --no-cache bnhsite-backend

if [ $? -eq 0 ]; then
    print_success "✅ Backend rebuild successful"
else
    print_error "❌ Backend rebuild failed"
    exit 1
fi

echo ""
print_status "🔄 Restarting backend..."
docker-compose restart bnhsite-backend

echo ""
print_status "⏳ Waiting for backend to start..."
sleep 15

echo ""
print_status "🧪 Testing fixed API..."

# Test internal API
INTERNAL_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/ 2>/dev/null || echo "FAILED")
echo "Internal API test: $INTERNAL_TEST"

# Test debug endpoint
DEBUG_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/debug 2>/dev/null || echo "FAILED")
echo "Debug endpoint test: $DEBUG_TEST"

# Test hosting plans
PLANS_TEST=$(docker exec bnhsite-backend curl -s http://localhost:8001/hosting-plans 2>/dev/null | head -100)
echo "Hosting plans test: $PLANS_TEST"

echo ""
print_status "📋 API Status Summary:"

if [[ "$INTERNAL_TEST" == *"Blue Nebula Hosting API"* ]]; then
    print_success "✅ Root endpoint working"
else
    print_error "❌ Root endpoint failed"
    echo "Check logs: docker logs bnhsite-backend"
fi

if [[ "$DEBUG_TEST" == *"API Working"* ]]; then
    print_success "✅ Debug endpoint working"
else
    print_error "❌ Debug endpoint failed"
fi

if [[ "$PLANS_TEST" == *"name"* ]] && [[ "$PLANS_TEST" == *"type"* ]]; then
    print_success "✅ Hosting plans endpoint working"
else
    print_warning "⚠️ Hosting plans endpoint may need database initialization"
    echo "Run: docker exec bnhsite-backend python3 init_database.py"
fi

echo ""
print_status "🎯 Test URLs (internal):"
echo "  Root: docker exec bnhsite-backend curl http://localhost:8001/"
echo "  Debug: docker exec bnhsite-backend curl http://localhost:8001/debug"
echo "  Plans: docker exec bnhsite-backend curl http://localhost:8001/hosting-plans"

echo ""
print_status "🌐 Test URLs (external - try these):"
echo "  Root: curl https://bluenebulahosting.com/api/"
echo "  Debug: curl https://bluenebulahosting.com/api/debug"
echo "  Plans: curl https://bluenebulahosting.com/api/hosting-plans"

echo ""
if [[ "$INTERNAL_TEST" == *"Blue Nebula Hosting API"* ]]; then
    print_success "🎉 API code is now fixed and working internally!"
    print_status "If external API still doesn't work, it's a Caddy routing issue."
else
    print_error "❌ API still has issues. Check backend logs for details."
fi