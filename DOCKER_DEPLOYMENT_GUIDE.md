# Blue Nebula Hosting - Docker Deployment Guide

## 🐳 Docker Production Setup

This repository includes a production-ready Docker configuration with optimized builds and security features.

### 📁 Architecture

```
Blue Nebula Hosting
├── backend/                 # FastAPI backend (Python 3.11)
│   ├── Dockerfile          # Multi-worker production setup
│   └── .dockerignore       # Optimized build context
├── frontend/               # React frontend (Node 18)
│   ├── Dockerfile          # Multi-stage build with Nginx
│   └── .dockerignore       # Optimized build context
└── docker-compose.yml      # Full stack orchestration
```

### 🚀 Quick Start

1. **Clone and Navigate:**
   ```bash
   cd /path/to/blue-nebula-hosting
   ```

2. **Configure Environment Variables:**
   ```bash
   # Backend - Update these with your secure values
   cp backend/.env.production backend/.env
   
   # Frontend - Update backend URL for your domain
   cp frontend/.env.production frontend/.env
   ```

3. **Update Security Credentials:**
   Edit `docker-compose.yml` and update:
   - MongoDB root password
   - JWT secret key
   - Uptime Kuma API key (if using)

4. **Build and Start:**
   ```bash
   docker-compose up -d --build
   ```

5. **Verify Services:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

### 🔧 Configuration

#### Required Environment Variables

**Backend (.env):**
```env
MONGO_URL=mongodb://admin:YOUR_MONGO_PASSWORD@mongodb:27017/blue_nebula_hosting?authSource=admin
DB_NAME=blue_nebula_hosting
JWT_SECRET_KEY=your_super_secure_jwt_secret_key_change_this
UPTIME_KUMA_API_KEY=your_uptime_kuma_api_key
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=https://your-domain.com/api
```

#### Caddy Configuration

Since you're using Caddy, here's a sample Caddyfile:

```caddy
your-domain.com {
    # Frontend
    handle /* {
        reverse_proxy localhost:3000
    }
    
    # Backend API
    handle /api/* {
        reverse_proxy localhost:8001
    }
    
    # Security headers
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
    
    # Enable compression
    encode gzip
    
    # Logging
    log {
        output file /var/log/caddy/access.log
    }
}
```

### 📊 Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React app with Nginx |
| Backend | 8001 | FastAPI with 4 workers |
| MongoDB | Internal | Database (not exposed) |

### 🔒 Security Features

- **Non-root users** in all containers
- **Security options** (`no-new-privileges`)
- **Health checks** for all services
- **MongoDB authentication** enabled
- **Nginx security headers**
- **Gzip compression** enabled
- **Static asset caching** optimized

### 🛠 Management Commands

```bash
# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart [service_name]

# Scale backend (if needed)
docker-compose up -d --scale backend=2

# Backup MongoDB
docker exec blue-nebula-mongodb mongodump --authenticationDatabase admin -u admin -p secure_password_change_this --out /tmp/backup

# Update and restart
docker-compose pull
docker-compose up -d --build

# Stop all services
docker-compose down

# Stop and remove volumes (DANGER: This deletes data)
docker-compose down -v
```

### 📈 Performance Optimizations

**Frontend:**
- Multi-stage build (removes dev dependencies)
- Nginx with gzip compression
- Static asset caching (1 year)
- React production build optimization

**Backend:**
- 4 uvicorn workers for concurrent processing
- Health checks for reliability
- Optimized Python dependencies
- Non-root security

**Database:**
- MongoDB 7.0 with authentication
- Persistent volumes for data
- Internal networking (not exposed externally)

### 🔍 Monitoring

Health checks are configured for all services:
- **Frontend:** HTTP check on port 3000
- **Backend:** HTTP check on port 8001  
- **MongoDB:** mongosh ping command

View health status:
```bash
docker-compose ps
```

### 🚨 Production Checklist

- [ ] Update all default passwords in `docker-compose.yml`
- [ ] Set secure JWT secret key
- [ ] Configure proper domain in frontend `.env`
- [ ] Set up Caddy reverse proxy
- [ ] Configure SSL certificates
- [ ] Set up log rotation
- [ ] Configure backup strategy for MongoDB
- [ ] Monitor resource usage
- [ ] Set up monitoring/alerting

### 🆘 Troubleshooting

**Services won't start:**
```bash
docker-compose logs [service_name]
```

**Database connection issues:**
```bash
docker exec -it blue-nebula-mongodb mongosh -u admin -p
```

**Frontend build fails:**
```bash
docker-compose build --no-cache frontend
```

**Clear everything and start fresh:**
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### 📞 Support

For issues with the Blue Nebula Hosting application, check:
1. Service logs: `docker-compose logs -f`
2. Health status: `docker-compose ps`
3. Resource usage: `docker stats`