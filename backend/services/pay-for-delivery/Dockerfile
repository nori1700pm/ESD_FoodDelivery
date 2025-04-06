FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pay-for-delivery/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files separately
COPY pay-for-delivery /app/pay-for-delivery
COPY pay-for-delivery/invokes.py /app/invokes.py
COPY rabbitmq /app/rabbitmq


# Expose the port
EXPOSE 5004

# Run the Flask app
CMD ["python", "pay-for-delivery/app.py"]