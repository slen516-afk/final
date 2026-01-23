# 使用官方的 Bun 映像檔
FROM oven/bun:1 as base

WORKDIR /app

# 1. 複製依賴描述檔
COPY package.json bun.lockb ./

# 2. 安裝依賴 (Bun 速度很快)
RUN bun install

# 3. 複製剩下的程式碼
COPY . .

# 4. 開放 Port (Vite 預設是 5173)
EXPOSE 5173

# 5. 啟動指令 (加上 --host 才能讓外部瀏覽器連得到 Docker 內的網頁)
CMD ["bun", "run", "dev", "--host"]