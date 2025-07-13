#!/bin/bash

echo "🚀 Blue Nebula Hosting - Complete Rebuild and Deploy"
echo "===================================================="

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

# Check if we're in the right directory
if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from your Blue Nebula Hosting directory"
    print_error "Make sure you have backend/ and frontend/ folders"
    exit 1
fi

print_status "Starting complete rebuild of Blue Nebula Hosting..."

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose stop bnhsite-frontend bnhsite-backend bnhsite-mongodb 2>/dev/null || true

# Remove existing containers
print_status "Removing existing containers..."
docker-compose rm -f bnhsite-frontend bnhsite-backend bnhsite-mongodb 2>/dev/null || true

# Build backend with all scripts included
print_status "Building backend (includes init scripts)..."
docker-compose build --no-cache bnhsite-backend

if [ $? -ne 0 ]; then
    print_error "Backend build failed!"
    exit 1
fi

# Build frontend with logos included
print_status "Building frontend (includes logos)..."
docker-compose build --no-cache bnhsite-frontend

if [ $? -ne 0 ]; then
    print_error "Frontend build failed!"
    exit 1
fi

# Start MongoDB first
print_status "Starting MongoDB..."
docker-compose up -d bnhsite-mongodb

# Wait for MongoDB to be healthy
print_status "Waiting for MongoDB to be ready..."
for i in {1..30}; do
    if docker-compose ps bnhsite-mongodb | grep -q "healthy"; then
        print_success "MongoDB is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "MongoDB failed to start properly"
        exit 1
    fi
    sleep 2
done

# Start backend
print_status "Starting backend..."
docker-compose up -d bnhsite-backend

# Wait for backend to be healthy
print_status "Waiting for backend to be ready..."
for i in {1..30}; do
    if docker-compose ps bnhsite-backend | grep -q "healthy"; then
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

# Start frontend
print_status "Starting frontend..."
docker-compose up -d bnhsite-frontend

# Wait for frontend to be healthy
print_status "Waiting for frontend to be ready..."
for i in {1..30}; do
    if docker-compose ps bnhsite-frontend | grep -q "healthy"; then
        print_success "Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start properly"
        print_error "Check logs: docker-compose logs bnhsite-frontend"
        exit 1
    fi
    sleep 2
done

# Test backend API
print_status "Testing backend API..."
sleep 5
API_RESPONSE=$(curl -s https://bluenebulahosting.com/api/ | jq -r '.message' 2>/dev/null)
if [ "$API_RESPONSE" = "Blue Nebula Hosting API" ]; then
    print_success "Backend API is working"
else
    print_warning "Backend API test failed or returned unexpected response"
    print_warning "Response: $API_RESPONSE"
fi

# Display final status
echo ""
print_success "🎉 Blue Nebula Hosting deployment completed!"
echo ""
print_status "Container Status:"
docker-compose ps bnhsite-mongodb bnhsite-backend bnhsite-frontend

echo ""
print_status "Next Steps:"
echo "1. Initialize database: ./init_db.sh"
echo "2. Change admin credentials: ./change_admin.sh"
echo "3. Test website: https://bluenebulahosting.com"
echo "4. Test admin panel: https://bluenebulahosting.com/admin"

echo ""
print_status "Useful Commands:"
echo "- View logs: docker-compose logs -f bnhsite-backend"
echo "- Restart service: docker-compose restart bnhsite-backend"
echo "- Enter container: docker exec -it bnhsite-backend bash"
echo "- Initialize DB: docker exec bnhsite-backend python3 init_database.py"
echo "- Change admin: docker exec -it bnhsite-backend python3 change_admin_credentials.py"