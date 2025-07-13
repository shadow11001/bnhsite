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
EOF
    
    print_success "Integration environment file created: .env.blue-nebula-generated"
}

# Check for existing docker-compose.yml
check_existing_compose() {
    if [ -f "docker-compose.yml" ]; then
        print_warning "Found existing docker-compose.yml"
        print_status "You'll need to manually integrate the services from docker-compose.services.yml"
        MANUAL_INTEGRATION=true
    else
        print_status "No existing docker-compose.yml found"
        MANUAL_INTEGRATION=false
    fi
}

# Check for port conflicts
check_port_conflicts() {
    print_status "Checking for port conflicts..."
    
    # Check if ports 3000 and 8001 are in use
    if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
        print_warning "Port 3000 is already in use. Consider changing BLUE_NEBULA_FRONTEND_PORT"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":8001 "; then
        print_warning "Port 8001 is already in use. Consider changing BLUE_NEBULA_BACKEND_PORT"
    fi
}

# Provide integration instructions
show_integration_instructions() {
    echo ""
    print_status "=== INTEGRATION INSTRUCTIONS ==="
    echo ""
    
    if [ "$MANUAL_INTEGRATION" = true ]; then
        print_status "MANUAL INTEGRATION REQUIRED:"
        echo "1. Copy the services from 'docker-compose.services.yml' into your existing docker-compose.yml"
        echo "2. Add the environment variables from '.env.blue-nebula-generated' to your .env file"
        echo "3. Adjust the build context paths to match your directory structure"
        echo "4. Update network configurations if needed"
        echo ""
        print_status "Service names to use:"
        echo "  - bnhsite-mongodb (database)"
        echo "  - bnhsite-backend (API server)"
        echo "  - bnhsite-frontend (React app)"
        echo ""
        print_status "Example integration:"
        echo "  services:"
        echo "    # ... your existing services ..."
        echo "    # Copy the bnhsite services here"
        echo ""
        echo "  volumes:"
        echo "    # ... your existing volumes ..."
        echo "    # Add bnhsite volumes"
        echo ""
        echo "  networks:"
        echo "    # ... your existing networks ..."
        echo "    # Add blue-nebula-network or use existing network"
    else
        print_status "NO EXISTING DOCKER-COMPOSE FOUND:"
        echo "You can use the provided docker-compose.services.yml as your main docker-compose.yml"
        echo "1. Copy docker-compose.services.yml to docker-compose.yml"
        echo "2. Add the environment variables from '.env.blue-nebula-generated' to a .env file"
    fi
    
    echo ""
    print_status "IMPORTANT STEPS AFTER INTEGRATION:"
    echo "1. Update build context paths in your docker-compose.yml to match your directory structure"
    echo "2. Change BLUE_NEBULA_BACKEND_URL to your domain: https://your-domain.com/api"
    echo "3. Update port mappings if there are conflicts with your existing services"
    echo "4. Configure your Caddy reverse proxy (see Caddyfile.example)"
    echo "5. Build and start services: docker-compose up -d --build bnhsite-backend bnhsite-frontend bnhsite-mongodb"
    echo "6. Initialize database: ./init_db.sh"
    echo "7. Change admin credentials: docker exec -it bnhsite-backend python3 change_admin_credentials.py"
    echo ""
}

# Save credentials for reference
save_credentials() {
    cat > .bnhsite-credentials << EOF
# Blue Nebula Hosting - Integration Credentials
# Generated on: $(date)

MongoDB Root Password: ${MONGO_PASSWORD}
JWT Secret Key: ${JWT_SECRET}

# Add these to your .env file:
MONGO_ROOT_PASSWORD=${MONGO_PASSWORD}
BLUE_NEBULA_JWT_SECRET=${JWT_SECRET}

# Container Names:
# - bnhsite-mongodb
# - bnhsite-backend  
# - bnhsite-frontend

# IMPORTANT: Keep this file secure and do not commit to version control!
EOF
    
    print_success "Credentials saved to .bnhsite-credentials"
    print_warning "Keep the .bnhsite-credentials file secure!"
}

# Create example integration docker-compose
create_example_integration() {
    print_status "Creating example integrated docker-compose.yml..."
    
    cat > docker-compose.example.yml << 'EOF'
version: '3.8'

services:
  # Example: Your existing services
  # your-app:
  #   image: your-app:latest
  #   ports:
  #     - "8080:8080"
  #   networks:
  #     - your-network

  # Blue Nebula Hosting Services (copy these to your docker-compose.yml)
  blue-nebula-mongodb:
    image: mongo:7.0
    container_name: blue-nebula-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: blue_nebula_hosting
    volumes:
      - blue_nebula_mongodb_data:/data/db
      - blue_nebula_mongodb_config:/data/configdb
    networks:
      - blue-nebula-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  blue-nebula-backend:
    build:
      context: ./backend  # Adjust this path to match your structure
      dockerfile: Dockerfile
    container_name: blue-nebula-backend
    restart: unless-stopped
    environment:
      - MONGO_URL=mongodb://admin:${MONGO_ROOT_PASSWORD}@blue-nebula-mongodb:27017/blue_nebula_hosting?authSource=admin
      - DB_NAME=blue_nebula_hosting
      - JWT_SECRET_KEY=${BLUE_NEBULA_JWT_SECRET}
      - UPTIME_KUMA_API_KEY=${BLUE_NEBULA_UPTIME_KEY}
    ports:
      - "${BLUE_NEBULA_BACKEND_PORT:-8001}:8001"
    depends_on:
      blue-nebula-mongodb:
        condition: service_healthy
    networks:
      - blue-nebula-network

  blue-nebula-frontend:
    build:
      context: ./frontend  # Adjust this path to match your structure
      dockerfile: Dockerfile
    container_name: blue-nebula-frontend
    restart: unless-stopped
    environment:
      - REACT_APP_BACKEND_URL=${BLUE_NEBULA_BACKEND_URL}
    ports:
      - "${BLUE_NEBULA_FRONTEND_PORT:-3000}:3000"
    depends_on:
      blue-nebula-backend:
        condition: service_healthy
    networks:
      - blue-nebula-network

volumes:
  # Your existing volumes
  blue_nebula_mongodb_data:
    driver: local
  blue_nebula_mongodb_config:
    driver: local

networks:
  # Your existing networks
  blue-nebula-network:
    driver: bridge
EOF
    
    print_success "Example docker-compose.yml created: docker-compose.example.yml"
}

# Main integration process
main() {
    echo ""
    check_dependencies
    generate_passwords
    create_integration_env
    check_existing_compose
    check_port_conflicts
    save_credentials
    create_example_integration
    show_integration_instructions
    
    echo ""
    print_success "🎉 Blue Nebula Hosting integration files prepared!"
    print_status "Next steps:"
    echo "1. Review the integration instructions above"
    echo "2. Check the DOCKER_DEPLOYMENT_GUIDE.md for detailed information"
    echo "3. Adjust build context paths to match your directory structure"
    echo "4. Update your Caddy configuration using Caddyfile.example"
}

# Add integration files to .gitignore if it exists
if [ -f .gitignore ]; then
    for file in ".blue-nebula-credentials" ".env.blue-nebula-generated"; do
        if ! grep -q "$file" .gitignore; then
            echo "$file" >> .gitignore
        fi
    done
fi

# Run main function
main