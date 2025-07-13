#!/bin/bash

# Blue Nebula Hosting - Production Deployment Script
# This script helps deploy the Blue Nebula Hosting application with Docker

set -e

echo "🚀 Blue Nebula Hosting - Docker Deployment Script"
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

# Update environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    # Backend environment
    cat > backend/.env << EOF
MONGO_URL=mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/blue_nebula_hosting?authSource=admin
DB_NAME=blue_nebula_hosting
JWT_SECRET_KEY=${JWT_SECRET}
UPTIME_KUMA_API_KEY=uk1_USvIQkci-6cYMA5VcOksKY7B1TzT7ul2zrvFOniq
EOF

    # Frontend environment (you'll need to update this with your domain)
    cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

    print_success "Environment files created"
}

# Update docker-compose.yml with generated passwords
update_compose_file() {
    print_status "Updating docker-compose.yml with secure credentials..."
    
    # Create a temporary file with updated passwords
    sed -e "s/secure_password_change_this/${MONGO_PASSWORD}/g" \
        -e "s/your_super_secure_jwt_secret_key_change_this/${JWT_SECRET}/g" \
        docker-compose.yml > docker-compose.yml.tmp
    
    mv docker-compose.yml.tmp docker-compose.yml
    
    print_success "docker-compose.yml updated with secure credentials"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop any existing services
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "healthy"; then
            print_success "Services are healthy"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Waiting for services..."
        sleep 10
        ((attempt++))
    done
    
    print_warning "Services may still be starting. Check with: docker-compose ps"
}

# Display service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8001"
    echo "Backend Health: http://localhost:8001/"
    
    echo ""
    print_status "Useful Commands:"
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo "Restart service: docker-compose restart [service_name]"
}

# Save credentials for reference
save_credentials() {
    cat > .deployment-credentials << EOF
# Blue Nebula Hosting - Deployment Credentials
# Generated on: $(date)

MongoDB Root Password: ${MONGO_PASSWORD}
JWT Secret Key: ${JWT_SECRET}

# IMPORTANT: Keep this file secure and do not commit to version control!
EOF
    
    print_success "Credentials saved to .deployment-credentials"
    print_warning "Keep the .deployment-credentials file secure!"
}

# Main deployment process
main() {
    echo ""
    check_dependencies
    generate_passwords
    setup_environment
    update_compose_file
    deploy_services
    wait_for_services
    show_status
    save_credentials
    
    echo ""
    print_success "🎉 Blue Nebula Hosting deployment completed!"
    print_status "Check the DOCKER_DEPLOYMENT_GUIDE.md for more information"
    print_warning "Don't forget to update the frontend REACT_APP_BACKEND_URL with your domain"
}

# Add .deployment-credentials to .gitignore if it exists
if [ -f .gitignore ]; then
    if ! grep -q ".deployment-credentials" .gitignore; then
        echo ".deployment-credentials" >> .gitignore
    fi
fi

# Run main function
main