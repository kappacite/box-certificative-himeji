# ── Dev stage ──────────────────────────────────────────────────
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies first (layer cache)
COPY package*.json .
RUN npm ci

# Copy source
COPY . .

EXPOSE 5173

# --host 0.0.0.0 required to be reachable outside the container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
