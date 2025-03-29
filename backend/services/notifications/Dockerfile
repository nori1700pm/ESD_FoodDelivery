FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY notifications/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy error service and shared rabbitmq code
COPY notifications /app/notifications
COPY rabbitmq /app/rabbitmq

# Expose the port
EXPOSE 6000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:6000/health || exit 1


# Run your app
CMD ["python", "notifications/app.py"]

# Run the app with Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]



# as reference from esd labs
# FROM python:3-slim
# WORKDIR /usr/src/app
# COPY http.reqs.txt ./
# RUN python -m pip install --no-cache-dir -r http.reqs.txt
# COPY ./order.py ./

