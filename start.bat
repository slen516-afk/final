@echo off
chcp 65001 >nul
echo [系統] 正在啟動專案...

:: 1. 啟動後端 (venv 就在 backend 裡面，所以不用 ..\)
echo [系統] 正在啟動後端 OCR 服務 (RTX 3070)...
start "Backend - Flask" cmd /k "cd backend && venv\Scripts\python.exe main.py"

:: 2. 啟動前端 (Bun)
echo [系統] 正在啟動前端介面...
cd frontend
bun run dev

pause