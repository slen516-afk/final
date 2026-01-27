@echo off
chcp 65001 >nul
echo [系統] 正在準備全線 Demo 環境...

:: 1. 啟動後端 Flask (顯示模型加載進度)
echo [1/3] 啟動後端 OCR 服務...
start "Backend-Server" cmd /k "cd backend && venv\Scripts\python.exe main.py"

:: 2. 啟動 Localtunnel 通道 (後端)
echo [2/3] 開啟後端對外通道...
start "Tunnel-Backend" cmd /k "npx localtunnel --port 5000"

:: 3. 啟動 Localtunnel 通道 (前端)
echo [3/3] 開啟前端對外通道...
start "Tunnel-Frontend" cmd /k "npx localtunnel --port 5173"

echo.
echo ======================================================
echo [重要提醒] 
echo 1. 請檢查 Tunnel-Backend 視窗給你的網址。
echo 2. 將網址填入 frontend/.env 的 VITE_API_URL 中。
echo 3. 完成後，回到這個視窗按任意鍵啟動前端。
echo ======================================================
pause

:: 4. 啟動前端 Vite
echo [最後一步] 啟動前端介面...
cd frontend
bun run dev

pause