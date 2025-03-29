FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY amqp_lib.py .
COPY amqp_setup.py .

# Expose the port
EXPOSE 5672
EXPOSE 15672

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5672/health || exit 1


CMD ["python", "amqp_setup.py"]


# Run the app with Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]