FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY kimai/ kimai/
COPY .env .

RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Run the server
CMD ["python", "-m", "kimai.kimai"]
