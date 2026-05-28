# ── Build stage ────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# System deps for bcrypt / compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create data directory for SQLite volume mount
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["flask", "--app", "app.py", "run", "--host", "0.0.0.0", "--port", "5000", "--debug"]
