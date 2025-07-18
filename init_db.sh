#!/bin/bash

# Blue Nebula Hosting - Database Initialization Script
# This script initializes the MongoDB database with default data

echo "🚀 Blue Nebula Hosting - Database Initialization"
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

# Check if backend container is running
print_status "Checking if backend container is running..."

if docker-compose ps | grep -q "bnhsite-backend.*Up"; then
    print_success "Backend container is running"
else
    print_error "Backend container is not running. Please start it first with:"
    echo "  docker-compose up -d bnhsite-backend"
    exit 1
fi

# Run the initialization script inside the backend container (script is already copied during build)
print_status "Running database initialization..."
docker exec bnhsite-backend python3 init_database.py

if [ $? -eq 0 ]; then
    print_success "🎉 Database initialization completed successfully!"
    echo ""
    print_status "Your Blue Nebula Hosting database now includes:"
    echo "  ✅ 36 Hosting plans (SSD Shared, HDD Shared, VPS, GameServers)"
    echo "  ✅ Website content (hero, about, features)"
    echo "  ✅ Navigation menu"
    echo "  ✅ Company information"
    echo "  ✅ Legal content (Terms of Service, Privacy Policy)"
    echo "  ✅ Site settings"
    echo "  ✅ Sample promo codes"
    echo ""
    print_status "You can now visit your website: https://bluenebulahosting.com"
    print_status "Admin panel: https://bluenebulahosting.com/admin (admin/admin123)"
else
    print_error "Database initialization failed. Check the logs above for details."
    exit 1
fi