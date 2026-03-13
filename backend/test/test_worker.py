import os
import sys
import time

# 設定路徑以便引入 app.py 及其中的函數
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
flask_dir = os.path.join(backend_dir, "flask")

if flask_dir not in sys.path:
    sys.path.insert(0, flask_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import check_worker_health

def test_health():
    print("--- 開始 Worker 健康檢查測試 ---")
    online, nodes = check_worker_health()
    if online:
        print(f"測試成功：Worker 在線，節點：{nodes}")
    else:
        print("測試提醒：Worker 目前離線（這在重新部署期間是正常的）")
    print("--- 測試結束 ---")

if __name__ == "__main__":
    test_health()