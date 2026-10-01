# ==============================================================================
# NexoraNet - Production Frontend Dockerfile
# Multi-stage, Lightweight Nginx Alpine Serving Pre-built SPA Assets
# ==============================================================================

# -----------------------------
# Stage 1: Build Frontend Assets
# -----------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies with lockfile caching
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Copy source and build static distribution bundle
COPY . .

ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# -----------------------------
# Stage 2: Serve via Nginx Alpine
# -----------------------------
FROM nginx:alpine AS runner

# Remove default nginx HTML boilerplate
RUN rm -rf /usr/share/nginx/html/*

# Copy custom production nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy pre-compiled production static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check probe
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

# Start Nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]
