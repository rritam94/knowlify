FROM python:3.10.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    iputils-ping \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY / /app/

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]