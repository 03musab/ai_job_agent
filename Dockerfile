# Multi-stage Docker build for AI JobSnap
# Stage 1: Build Frontend Assets (Tailwind CSS)
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tailwind.config.js ./
COPY static/ ./static/
COPY templates/ ./templates/
RUN npm run build:css

# Stage 2: Production Python Image
FROM python:3.12-slim
WORKDIR /app

# Install essential OS packages for SQLite & networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code & compiled CSS from Stage 1
COPY . .
COPY --from=frontend-builder /app/static/css/output.css ./static/css/output.css

# Expose port
ENV PORT=5000
EXPOSE 5000

# Default entrypoint runs Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
