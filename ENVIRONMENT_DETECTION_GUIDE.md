# Environment Detection Configuration Guide

## Overview
The frontend now automatically detects whether it's running in development or production environment and sets the appropriate API URL accordingly.

## How It Works

### 1. Automatic Environment Detection
The frontend uses the following logic to determine the API URL:

1. **Environment Variable Override**: If `REACT_APP_BACKEND_URL` is set, it uses that value
2. **Hostname-based Detection**: If no env var is set, it detects based on hostname:
   - **Development**: `dev.`, `localhost`, or `127.0.0.1` → `https://dev.bluenebulahosting.com`
   - **Production**: All other hostnames → `https://bluenebulahosting.com`

### 2. Environment Variables

#### For Development Environment
Set these in your `.env` or docker-compose environment:
```bash
ENVIRONMENT=dev
NODE_ENV=development
BLUE_NEBULA_BACKEND_URL=  # Leave empty for auto-detection
```

#### For Production Environment
Set these in your `.env` or docker-compose environment:
```bash
ENVIRONMENT=prod
NODE_ENV=production
BLUE_NEBULA_BACKEND_URL=  # Leave empty for auto-detection
```

#### Manual Override (Optional)
To manually specify the backend URL:
```bash
BLUE_NEBULA_BACKEND_URL=https://custom.domain.com
```

## Configuration Examples

### Development Setup
1. Copy `.env.blue-nebula` to `.env` in your project root
2. Set `ENVIRONMENT=dev`
3. Deploy with docker-compose - frontend will automatically call `dev.bluenebulahosting.com/api`

### Production Setup
1. Copy `.env.blue-nebula` to `.env` in your project root  
2. Set `ENVIRONMENT=prod`
3. Deploy with docker-compose - frontend will automatically call `bluenebulahosting.com/api`

## Troubleshooting

### Console Debugging
The frontend will log the detected API URL to browser console. Check for:
```
API URL detected: https://dev.bluenebulahosting.com
```

### Common Issues
1. **Still getting 404s**: Check backend is running and accessible at the detected URL
2. **CORS errors**: Ensure backend CORS configuration allows requests from your frontend domain
3. **Wrong API URL**: Verify hostname detection or set `REACT_APP_BACKEND_URL` explicitly

### Verification
Test the environment detection by checking browser console or network tab to see which API endpoints are being called.

## Files Changed
- `frontend/src/App.js` - Added environment detection logic
- `frontend/src/AdminPanel.js` - Added environment detection logic  
- `docker-compose.services.yml` - Added environment variables
- `frontend/Dockerfile` - Added build args for environment variables
- `.env.blue-nebula` - Updated with environment configuration
- `frontend/.env` and `frontend/.env.production` - Updated for auto-detection