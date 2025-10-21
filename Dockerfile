FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates supervisor procps coreutils \
    && rm -rf /var/lib/apt/lists/*
# Setting project root and installing dependencies
FROM base AS dev-deps
WORKDIR /app
COPY requirements.txt .
COPY supervisord.conf .
COPY mcp-config.json .
COPY proxy.py .
RUN pip install --no-cache-dir -r requirements.txt 
RUN curl -fsSL https://ollama.com/install.sh | sh
# Copying source code and environment variables
COPY kimai/ kimai/
COPY ui/ ui/
COPY .env .

RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

RUN mkdir /app/mcp_context

# # Healthcheck: ping the bridge once it's up
# HEALTHCHECK --interval=10s --timeout=3s --retries=10 \
#     CMD curl -fsS http://localhost:11435/health || exit 1

EXPOSE 8080 11435 11434
CMD ["supervisord", "-c", "/app/supervisord.conf"]
