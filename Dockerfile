FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1

# Setting project root and installing dependencies
FROM base AS dev-deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copying source code and environment variables
COPY kimai/ kimai/
COPY .env .

RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Run the server
CMD ["python", "-m", "kimai.kimai"]
