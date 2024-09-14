FROM python:3.10.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the Google Application Credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_key.json"

# Install dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service_key.json file for Google Text-to-Speech
COPY service_key.json /app/

# Copy application code
COPY / /app/

# Command to run the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:80", "-k", "eventlet", "app:app"]
