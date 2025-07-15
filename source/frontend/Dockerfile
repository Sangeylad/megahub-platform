# /var/www/megahub/source/frontend/Dockerfile

# ==========================================
# MegaHub Frontend - Production Dockerfile React 19 + Lightning CSS
# ==========================================

FROM node:20-alpine AS base
RUN addgroup --system --gid 1001 megahub && adduser --system --uid 1001 megahub
RUN apk add --no-cache libc6-compat curl ca-certificates python3 make g++
WORKDIR /app

# ==========================================
# Dependencies Installation
# ==========================================
FROM base AS deps
COPY package*.json ./
# Nettoyer le cache npm avant installation
RUN npm cache clean --force
RUN npm ci --frozen-lockfile --no-audit --no-fund
RUN npm cache clean --force

# ==========================================
# Builder React 19 + Lightning CSS + React Compiler
# ==========================================
FROM base AS builder
WORKDIR /app

# Copier dependencies depuis deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/package*.json ./

# Copier source code
COPY . .

# Variables build production React 19
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV VITE_BUILD_MODE=production
ENV VITE_API_BASE_URL=https://backoffice.humari.fr
ENV VITE_ENABLE_REACT_COMPILER=true
ENV VITE_ENABLE_LIGHTNING_CSS=true

# Build avec vérifications
RUN echo "🔨 Starting build process..."
RUN npm run build

# Vérifications build success
RUN test -d dist || (echo "❌ Build failed - dist directory not found" && exit 1)
RUN test -f dist/index.html || (echo "❌ Build failed - index.html not found" && exit 1)
RUN echo "✅ Build completed successfully"
RUN echo "📊 Build size: $(du -sh dist | cut -f1)"

# ==========================================
# Production nginx Server React 19 Ready
# ==========================================
FROM nginx:1.27-alpine AS runner

LABEL maintainer="MegaHub Team <tech@megahub.fr>"
LABEL version="3.0.0"
LABEL description="MegaHub Frontend - Production nginx with React 19 + Lightning CSS"

# Sécurité : Updates système
RUN apk upgrade --no-cache

# Configuration nginx optimisée pour React 19 + SPA
COPY <<EOF /etc/nginx/nginx.conf
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # MIME Types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    server {
        listen 80;
        root /usr/share/nginx/html;
        index index.html;
        
        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # Static assets cache (React 19 chunks)
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary "Accept-Encoding";
        }
        
        # React Router - SPA fallback
        location / {
            try_files \$uri \$uri/ /index.html;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires "0";
        }
        
        # Health check endpoint
        location /health {
            return 200 "healthy React 19 frontend\n";
            add_header Content-Type text/plain;
        }
        
        # API proxy (optionnel)
        location /api/ {
            return 404 "API calls should go directly to backend";
        }
    }
}
EOF

# Copier les assets buildés React 19
COPY --from=builder /app/dist /usr/share/nginx/html

# Vérifier que les fichiers sont bien copiés
RUN ls -la /usr/share/nginx/html/
RUN test -f /usr/share/nginx/html/index.html || (echo "❌ index.html not found in nginx" && exit 1)

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]