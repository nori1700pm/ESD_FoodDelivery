FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files separately
COPY app.py .
COPY invokes.py .

# Expose the port
EXPOSE 5003

# Run the Flask app
CMD ["python", "app.py"]