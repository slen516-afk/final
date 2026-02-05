FROM python:3.10-slim

WORKDIR /app

# 安裝系統依賴 (如果需要)
RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼 (在開發模式下，這步常被 Volume 覆蓋，但為了 Production 還是要寫)
COPY . .