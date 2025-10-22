FROM python:3.12-slim AS base

# Setting project root and installing dependencies
FROM base AS dev-deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copying source code and environment variables
COPY kimai/ kimai/

RUN useradd -m -u 1000 mcpuser 
RUN chown -R mcpuser:mcpuser /app

# Run the server
USER mcpuser
CMD ["python", "kimai/server.py"]
