# Frontend Development Dockerfile for NexoraNet
FROM node:22-alpine

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY package.json ./
RUN npm install

# Copy application source
COPY . .

# Expose Vite development server port
EXPOSE 5173

# Start development server binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
