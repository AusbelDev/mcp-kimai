# Builder stage
FROM python:3.12-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base libffi-dev

COPY requirements.txt .

# Create venv and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-alpine

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY kimai/ kimai/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    XDG_CONFIG_HOME="/home/mcpuser/.config" \
    MSAL_CACHE_DIR="/home/mcpuser/.config/msal"

# Create user and setup permissions
RUN adduser -D -u 1000 mcpuser && \
    mkdir -p /home/mcpuser/.config/msal && \
    chown -R mcpuser:mcpuser /home/mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

CMD ["python", "kimai/server.py"]