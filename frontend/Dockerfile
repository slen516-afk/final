# /frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# 先複製 package.json 方便利用 Docker 緩存機制加速安裝
COPY package.json package-lock.json* ./

# 安裝依賴套件
RUN npm install

# 複製其餘程式碼
COPY . .

# 暴露 3000 port
EXPOSE 3000

# 啟動開發伺服器，並強制指定 host 與 port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]