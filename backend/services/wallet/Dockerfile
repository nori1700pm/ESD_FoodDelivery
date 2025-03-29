FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY wallet/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Correct path to wallet/app.py and rabbitmq directory
COPY wallet /app/wallet
COPY rabbitmq /app/rabbitmq

# Expose the port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5002/health || exit 1

# Run with Gunicorn using module path
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "wallet.app:app"]