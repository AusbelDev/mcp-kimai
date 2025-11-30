FROM python:3.12-alpine

# Setting project root and installing dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copying source code and environment variables
COPY kimai/ kimai/

RUN adduser -D -u 1000 mcpuser && chown -R mcpuser:mcpuser /app && mkdir -p /home/mcpuser/.config/msal

# Run the server
USER mcpuser
CMD ["python", "kimai/server.py"]
