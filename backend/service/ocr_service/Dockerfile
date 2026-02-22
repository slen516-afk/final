FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# 這裡安裝 pandas, scikit-learn, tensorflow 等
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "ocr_service.py"]