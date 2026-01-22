FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# 這裡安裝 pandas, scikit-learn, tensorflow 等
RUN pip install --no-cache-dir -r requirements.txt

COPY . .