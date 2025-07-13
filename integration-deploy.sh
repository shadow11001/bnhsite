#!/bin/bash

# Blue Nebula Hosting - Integration Script for Existing Docker Compose
# This script helps integrate Blue Nebula Hosting into your existing docker-compose setup

set -e

echo "🚀 Blue Nebula Hosting - Docker Integration Script"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Generate secure passwords
generate_passwords() {
    print_status "Generating secure passwords..."
    
    MONGO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    
    print_success "Secure passwords generated"
}

# Create integration environment file
create_integration_env() {
    print_status "Creating integration environment file..."
    
    cat > .env.blue-nebula-generated << EOF
# Blue Nebula Hosting - Generated Environment Variables
# Generated on: $(date)

# MongoDB Configuration
MONGO_ROOT_PASSWORD=${MONGO_PASSWORD}

# Blue Nebula Backend Configuration  
BLUE_NEBULA_JWT_SECRET=${JWT_SECRET}
BLUE_NEBULA_UPTIME_KEY=uk1_USvIQkci-6cYMA5VcOksKY7B1TzT7ul2zrvFOniq

# Port Configuration (customize if needed to avoid conflicts)
BLUE_NEBULA_FRONTEND_PORT=3000
BLUE_NEBULA_BACKEND_PORT=8001

# Frontend Backend URL (update with your domain)
BLUE_NEBULA_BACKEND_URL=http://localhost:8001

# IMPORTANT: Add these variables to your existing .env file
# Or source this file: source .env.blue-nebula-generated
