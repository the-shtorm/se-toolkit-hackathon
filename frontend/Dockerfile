FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (ci is faster and more reliable)
RUN npm ci --no-audit --no-fund

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Default command
CMD ["npm", "run", "dev"]
