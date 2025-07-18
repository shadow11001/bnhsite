# Multi-stage build for optimized React frontend
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies with exact versions for reproducible builds
RUN yarn install --frozen-lockfile --network-timeout 300000

# Copy all source code including public folder
COPY . .

# Accept build arguments for environment variables
ARG REACT_APP_BACKEND_URL
ARG NODE_ENV=production
ARG ENVIRONMENT=dev

# Set environment variables for build
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL}
ENV NODE_ENV=${NODE_ENV}
ENV ENVIRONMENT=${ENVIRONMENT}

# Build the application for production
RUN yarn build

# Production stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]