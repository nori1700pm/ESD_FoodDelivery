FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose the port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5001/health || exit 1

# Run the app with Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]



# as reference from esd labs
# FROM python:3-slim
# WORKDIR /usr/src/app
# COPY http.reqs.txt ./
# RUN python -m pip install --no-cache-dir -r http.reqs.txt
# COPY ./order.py ./
CMD [ "python", "./app.py" ]