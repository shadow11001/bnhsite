# Blue Nebula Hosting - Docker Integration Guide

## 🐳 Adding Blue Nebula Hosting to Your Existing Docker Setup

This guide helps you integrate the Blue Nebula Hosting application into your existing docker-compose.yml setup.

### 📁 Integration Files

```
Blue Nebula Hosting Integration
├── docker-compose.services.yml    # Service definitions to copy
├── .env.blue-nebula               # Environment variables
├── backend/Dockerfile             # Backend container
├── frontend/Dockerfile            # Frontend container
└── integration-deploy.sh          # Automated integration script
```

### 🚀 Quick Integration

#### Option 1: Automated Integration (Recommended)
```bash
# Run the integration script
./integration-deploy.sh
```

#### Option 2: Manual Integration

1. **Copy Service Definitions:**
   Copy the services from `docker-compose.services.yml` into your existing `docker-compose.yml` file.

2. **Add Environment Variables:**
   Add the variables from `.env.blue-nebula` to your existing `.env` file.

3. **Update File Paths:**
   Adjust the build context paths in the service definitions to match your directory structure.

### 📋 Manual Integration Steps

#### 1. Add to Your docker-compose.yml

Add these services to your existing `docker-compose.yml`:

```yaml
services:
  # ... your existing services ...

  # Blue Nebula Hosting Services
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
      context: ./blue-nebula-hosting/backend  # Adjust path as needed
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
      context: ./blue-nebula-hosting/frontend  # Adjust path as needed
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

# Add to your volumes section
volumes:
  # ... your existing volumes ...
  blue_nebula_mongodb_data:
    driver: local
  blue_nebula_mongodb_config:
    driver: local

# Add to your networks section
networks:
  # ... your existing networks ...
  blue-nebula-network:
    driver: bridge
```

#### 2. Add Environment Variables

Add these to your `.env` file:

```env
# Blue Nebula Hosting Configuration
MONGO_ROOT_PASSWORD=your_secure_mongo_password_here
BLUE_NEBULA_JWT_SECRET=your_super_secure_jwt_secret_here
BLUE_NEBULA_UPTIME_KEY=uk1_USvIQkci-6cYMA5VcOksKY7B1TzT7ul2zrvFOniq

# Port Configuration (optional, defaults shown)
BLUE_NEBULA_FRONTEND_PORT=3000
BLUE_NEBULA_BACKEND_PORT=8001

# Update with your domain
BLUE_NEBULA_BACKEND_URL=https://your-domain.com/api
```

#### 3. Adjust Build Context Paths

Update the `context` paths in the service definitions to match where you place the Blue Nebula files:

```yaml
# If you put the files in a subfolder
blue-nebula-backend:
  build:
    context: ./path/to/blue-nebula-hosting/backend

blue-nebula-frontend:
  build:
    context: ./path/to/blue-nebula-hosting/frontend
```

### 🔧 Network Integration

#### Option A: Use Existing Network
If you want to use your existing network instead of creating a new one:

```yaml
# Replace 'blue-nebula-network' with your existing network name
networks:
  - your-existing-network
```

#### Option B: Connect to Multiple Networks
If you need the services on multiple networks:

```yaml
networks:
  - your-existing-network
  - blue-nebula-network
```

### 🔒 Security Configuration

#### Generate Secure Passwords
```bash
# MongoDB password
openssl rand -base64 32 | tr -d "=+/" | cut -c1-25

# JWT secret
openssl rand -base64 64 | tr -d "=+/" | cut -c1-50
```

#### Update Environment Variables
Replace the default values in your `.env` file with the generated secure passwords.

### 🎯 Caddy Integration

Since you use Caddy, add this to your Caddyfile:

```caddy
your-domain.com {
    # Blue Nebula Frontend
    handle /hosting/* {
        uri strip_prefix /hosting
        reverse_proxy blue-nebula-frontend:3000
    }
    
    # Blue Nebula Backend API  
    handle /api/hosting/* {
        uri strip_prefix /hosting
        reverse_proxy blue-nebula-backend:8001
    }
    
    # Or serve as main site
    handle /* {
        reverse_proxy blue-nebula-frontend:3000
    }
    
    handle /api/* {
        reverse_proxy blue-nebula-backend:8001
    }
}
```

### 🛠 Management Commands

```bash
# Start Blue Nebula services
docker-compose up -d blue-nebula-mongodb blue-nebula-backend blue-nebula-frontend

# Stop Blue Nebula services
docker-compose stop blue-nebula-mongodb blue-nebula-backend blue-nebula-frontend

# View Blue Nebula logs
docker-compose logs -f blue-nebula-backend blue-nebula-frontend

# Restart Blue Nebula services
docker-compose restart blue-nebula-backend blue-nebula-frontend

# Remove Blue Nebula services (keeps data)
docker-compose rm -s blue-nebula-backend blue-nebula-frontend

# Remove all Blue Nebula data (DANGER: This deletes the database)
docker-compose down -v
docker volume rm blue_nebula_mongodb_data blue_nebula_mongodb_config
```

### 📊 Service Information

| Service | Container Name | Default Port | Purpose |
|---------|---------------|--------------|---------|
| Frontend | blue-nebula-frontend | 3000 | React app with Nginx |
| Backend | blue-nebula-backend | 8001 | FastAPI with 4 workers |
| MongoDB | blue-nebula-mongodb | Internal | Database (not exposed) |

### 🔍 Verification

After integration, verify everything is working:

```bash
# Check service status
docker-compose ps | grep blue-nebula

# Check health
docker-compose exec blue-nebula-backend curl -f http://localhost:8001/
docker-compose exec blue-nebula-frontend curl -f http://localhost:3000/

# Check logs for errors
docker-compose logs blue-nebula-backend
docker-compose logs blue-nebula-frontend
```

### 🚨 Common Issues

**Build Context Errors:**
- Ensure the `context` paths point to the correct directories
- Check that Dockerfile exists in the specified paths

**Network Issues:**
- Make sure the network name matches across all services
- Verify your existing networks don't conflict

**Port Conflicts:**
- Change `BLUE_NEBULA_FRONTEND_PORT` and `BLUE_NEBULA_BACKEND_PORT` if needed
- Check for port conflicts with your existing services

**Environment Variables:**
- Ensure all required variables are set in your `.env` file
- Generate secure passwords for production use

### 📞 Support

If you encounter issues:
1. Check service logs: `docker-compose logs [service_name]`
2. Verify environment variables are loaded
3. Ensure build contexts point to correct directories
4. Check for port conflicts with existing services