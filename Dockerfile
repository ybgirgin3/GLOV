# Python image kullan
FROM python:3.10-slim

# Çalışma dizini olarak /app klasörünü ayarla
WORKDIR /app

# Gerekli bağımlılıkları yükle
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY ./app /app

# Uvicorn ile FastAPI'yi çalıştır
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
