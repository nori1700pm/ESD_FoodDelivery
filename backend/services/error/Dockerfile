FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY error/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy error service and shared rabbitmq code
COPY error /app/error
COPY rabbitmq /app/rabbitmq


# Run the consumer directly with Python
CMD ["python", "error/app.py"]
