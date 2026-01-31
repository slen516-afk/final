import subprocess
import os
import time
import webbrowser
import sys

# ================= 設定區 =================
ENV_FILE_PATH = os.path.join("frontend", ".env")
ENV_VAR_NAME = "VITE_API_URL"
# 👇 Docker 內部也是對應到這個 Port，所以維持不變
LOCAL_API_URL = "http://localhost:5000"

# Docker 設定
DOCKER_IMAGE_NAME = "final-feature-app"
DOCKER_CONTAINER_NAME = "final-feature-running"

# 指令設定 (改為 Docker 指令)
# 1. 停止並刪除舊的容器 (如果有殘留)
CMD_KILL_OLD = f"docker rm -f {DOCKER_CONTAINER_NAME}"
# 2. 建置映像檔 (如果程式碼有改，這步會更新 Image)
CMD_BUILD = f"docker build -t {DOCKER_IMAGE_NAME} ."
# 3. 啟動容器 (對應 Port 5000 和 5173)
CMD_RUN = f"docker run -it --rm --gpus all -p 5000:5000 -p 5173:5173 --name {DOCKER_CONTAINER_NAME} {DOCKER_IMAGE_NAME}"
# =========================================

def update_env_file(url):
    """
    強制把 .env 改成指定的網址。
    雖然是在 Docker 內跑，但因為 Dockerfile 會 COPY 這個檔案，
    所以我們先在外面改好，打包進去才會是對的。
    """
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
            
        print(f"✅ [設定] 已將前端連線目標鎖定為: {url}")
        return True
    except Exception as e:
        print(f"❌ [錯誤] 更新 .env 失敗: {e}")
        return False

def check_docker_installed():
    """檢查是否有安裝 Docker"""
    try:
        subprocess.run("docker --version", shell=True, check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("--- [系統] 啟動 Docker 全自動模式 ---")
    print("🚀 這個模式將把前後端打包在容器中執行，徹底解決環境問題！")

    # 0. 檢查 Docker
    if not check_docker_installed():
        print("\n❌ 錯誤：找不到 Docker！")
        print("請先安裝 Docker Desktop 並啟動它：https://www.docker.com/products/docker-desktop/")
        input("按 Enter 鍵退出...")
        return

    # 1. 強制設定 .env (這樣打包進去的設定才會是對的)
    if update_env_file(LOCAL_API_URL):
        
        print("\n🧹 清理舊的容器 (如果有)...")
        subprocess.run(CMD_KILL_OLD, shell=True, stderr=subprocess.DEVNULL)

        print("🔨 正在建置/更新 Docker 映像檔 (第一次會比較久，請耐心等待)...")
        # 執行 Build
        build_result = subprocess.run(CMD_BUILD, shell=True)
        
        if build_result.returncode == 0:
            print("\n🔥 建置完成，正在啟動服務...")
            print("💡 啟動後，請注意看終端機顯示的 Log")
            
            # 自動開啟瀏覽器
            print("🌐 3秒後自動開啟瀏覽器...")
            time.sleep(10)
            webbrowser.open("http://localhost:5173")

            # 執行 Run (這會佔用目前的終端機視窗，直到你按 Ctrl+C)
            subprocess.run(CMD_RUN, shell=True)
        else:
            print("❌ 建置失敗，請檢查 Dockerfile 是否存在或有錯誤。")
            input("按 Enter 鍵退出...")
        
    else:
        print("❌ 設定檔更新失敗，未啟動服務。")

if __name__ == "__main__":
    main()