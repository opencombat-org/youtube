FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update \n && apt-get install -y --no-install-recommends ffmpeg ca-certificates \n && rm -rf /var/lib/apt/lists/*

# Copiar dependencias primero para cache
COPY web/ytdlp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código
COPY web/ytdlp /app

ENV PYTHONUNBUFFERED=1
ENV APP_STORAGE=/data

VOLUME ["/data"]

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
