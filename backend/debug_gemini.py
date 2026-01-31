import sys
import os
from dotenv import load_dotenv

# 1. 檢查 Python 是從哪裡執行的 (確認是否在 venv 裡)
print(f"🐍 Python 執行路徑: {sys.executable}")

try:
    import google.generativeai as genai
    # 2. 檢查套件版本 (這行最重要！如果版本低於 0.5.0 就找不到 flash)
    print(f"📦 套件版本: {genai.__version__}")
except ImportError:
    print("❌ 嚴重錯誤: 找不到 google-generativeai 套件！")
    sys.exit(1)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ 錯誤: 找不到 GEMINI_API_KEY，請檢查 .env 檔案")
else:
    print(f"🔑 API Key 前五碼: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    
    print("\n📋 === 你的帳號能用的模型列表 ===")
    try:
        found_flash = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
                if "flash" in m.name:
                    found_flash = True
        
        if found_flash:
            print("\n✅ 恭喜！你的環境支援 Flash 模型！")
        else:
            print("\n⚠️ 警告：列表中沒看到 Flash，可能版本過舊或區域限制。")
            
    except Exception as e:
        print(f"❌ 連線失敗: {e}")