#!/bin/bash

# 1. 啟動後端 (在背景執行，加上 & 符號)
echo "🔥 Starting Backend..."
cd /app/backend
python main.py &

# 2. 等待幾秒讓後端先跑起來
sleep 2

# 3. 啟動前端 (同樣在背景執行，必須加 --host 才能被瀏覽器連到)
echo "🚀 Starting Frontend..."
cd /app/frontend
npm run dev -- --host &

# 4. 讓容器保持運作 (等待上述任何一個進程結束)
wait -n