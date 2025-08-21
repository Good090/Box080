# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps: ffmpeg for merging streams
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create download dir
RUN mkdir -p /data
VOLUME ["/data"]

ENV DOWNLOAD_DIR=/data

# Provide timezone via env
ENV TZ=UTC

CMD ["python", "-m", "app.bot"]