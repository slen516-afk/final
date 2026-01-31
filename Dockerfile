# === 基礎映像檔 ===
FROM python:3.9-slim-bookworm

# === 第一步：安裝系統工具 ===
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# 設定工作目錄
WORKDIR /app

# === 第二步：安裝後端 ===
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# === 第三步：安裝前端 (修復重點區) ===
COPY frontend/package.json /app/frontend/
WORKDIR /app/frontend

# 🔥 關鍵修改：
# 在安裝前，強制從清單中刪除 Windows 專用套件
# 這樣 npm 就不會試圖去安裝它，也不會報錯了
RUN npm pkg delete dependencies.@swc/core-win32-x64-msvc \
    devDependencies.@swc/core-win32-x64-msvc \
    optionalDependencies.@swc/core-win32-x64-msvc

# 現在清單乾淨了，可以安心安裝
RUN npm install

# === 第四步：複製程式碼 ===
WORKDIR /app
COPY . /app

# 設定環境變數與權限
ENV PYTHONPATH="/app"
RUN chmod +x /app/entrypoint.sh

# === 啟動 ===
EXPOSE 5000 5173
CMD ["/bin/bash", "/app/entrypoint.sh"]