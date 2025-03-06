# Stage 1: Development environment
FROM node:18-alpine AS build
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache curl bash git

# Copy package files for better layer caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy rest of the application code
# In development, this will be mounted as a volume
COPY . .

# Set environment variables for development
ENV NODE_ENV=development
ENV VITE_API_URL=/api/v1

# Expose port for development server
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]

# Stage 2: Builder for production artifacts
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package files for better layer caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Set production environment
ENV NODE_ENV=production
ENV VITE_API_URL=/api/v1

# Build the application
RUN npm run build

# Stage 3: Production environment
FROM nginx:alpine AS production
WORKDIR /usr/share/nginx/html

# Create Nginx configuration with security best practices
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Enable compression \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript; \
    \
    # Add security headers \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
    add_header Referrer-Policy "strict-origin-when-cross-origin" always; \
    \
    # Set caching for static assets \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ { \
        expires 30d; \
        add_header Cache-Control "public, no-transform"; \
    } \
    \
    # Proxy API requests to backend service \
    location /api/ { \
        proxy_pass http://api:8000/api/; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
        proxy_read_timeout 90; \
    } \
    \
    # Handle Single Page Application routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist .

# Expose port for web traffic
EXPOSE 80

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]