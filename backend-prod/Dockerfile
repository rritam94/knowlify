FROM python:3.10.2-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_key.json"

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY service_key.json /app/
COPY / /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4", "--loop", "uvloop"]
