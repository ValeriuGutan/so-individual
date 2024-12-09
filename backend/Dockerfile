FROM python:3.11-slim

WORKDIR /app

# Instalăm curl pentru healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instalăm dependențele
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Creăm directorul pentru date
RUN mkdir -p /app/data

# Copiem codul aplicației
COPY app app/

# Expunem portul
EXPOSE 8000

# Comanda de pornire
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 