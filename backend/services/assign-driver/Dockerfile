FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY assign-driver/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files separately
COPY assign-driver /app/assign-driver
COPY assign-driver/invokes.py /app/invokes.py
COPY rabbitmq /app/rabbitmq

# Expose the port
EXPOSE 5006

# Run the Flask app
CMD ["python", "assign-driver/app.py"]