import subprocess
import os
import time
import sys

# ================= 設定區 =================
ENV_FILE_PATH = os.path.join("frontend", ".env")
ENV_VAR_NAME = "VITE_API_URL"
# 👇 直接鎖定本機網址 (解決上傳問題的關鍵)
LOCAL_API_URL = "http://127.0.0.1:5000"

# 指令設定
CMD_BACKEND_SERVER = 'start "Backend-Server" cmd /k "cd backend && venv\\Scripts\\python.exe main.py"'
CMD_FRONTEND_DEV = 'start "Frontend-Vite" cmd /k "cd frontend && bun run dev"'
# =========================================

def update_env_file(url):
    """強制把 .env 改成指定的網址"""
    try:
        lines = []
        if os.path.exists(ENV_FILE_PATH):
            with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        new_lines = []
        found = False
        
        for line in lines:
            if line.strip().startswith(f"{ENV_VAR_NAME}="):
                new_lines.append(f"{ENV_VAR_NAME}={url}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"{ENV_VAR_NAME}={url}\n")

        with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        print(f"✅ 已將前端連線目標鎖定為: {url}")
        return True
    except Exception as e:
        print(f"❌ 更新 .env 失敗: {e}")
        return False

def main():
    print("--- [系統] 啟動本機開發模式 (無 Tunnel) ---")
    print("🚀 這個模式最穩定，不會有檔案上傳大小限制")

    # 1. 強制設定 .env 為 127.0.0.1
    if update_env_file(LOCAL_API_URL):
        
        print("🔥 正在啟動後端與前端...")
        
        # 2. 啟動後端 Flask
        subprocess.Popen(CMD_BACKEND_SERVER, shell=True)
        time.sleep(1) 
        
        # 3. 啟動前端 Vite
        subprocess.Popen(CMD_FRONTEND_DEV, shell=True)
        
        print("\n✨ 服務已啟動！")
        print("💡 請直接去瀏覽器操作，上傳功能現在應該正常了。")
        
    else:
        print("❌ 設定檔更新失敗，未啟動服務。")

if __name__ == "__main__":
    main()