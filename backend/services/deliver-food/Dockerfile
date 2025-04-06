FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY deliver-food/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files separately
COPY deliver-food /app/deliver-food
COPY deliver-food/invokes.py /app/invokes.py
COPY rabbitmq /app/rabbitmq

# Expose the port
EXPOSE 5004

# Run the Flask app
CMD ["python", "deliver-food/app.py"]