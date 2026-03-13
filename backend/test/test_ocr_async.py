import os
import time
import uuid
import json
import sys
from celery import Celery

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Force local Redis URL for host testing
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
from core.redis_client import redis_client

def test_ocr_async():
    print(f"🔗 正在連接 Redis Broker: {os.environ['REDIS_URL']}...")
    app = Celery('ocr_test', broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    
    # 容器內的路徑（假設已透過 Volume 掛載）
    test_file = "/app/uploads/test_resume.pdf"
    
    # 在宿主機建立該檔案以便 Volume 同步（如果掛載了的話）
    host_file = os.path.abspath(os.path.join(os.getcwd(), 'backend', 'uploads', 'test_resume.pdf'))
    if not os.path.exists(host_file):
        os.makedirs(os.path.dirname(host_file), exist_ok=True)
        with open(host_file, 'w') as f:
            f.write("Dummy PDF content for connectivity test")
        print(f"📝 建立測試 dummy 檔案: {host_file}")

    job_id = f"ocr_test_{uuid.uuid4().hex[:8]}"
    print(f"\n🚀 正在發送 OCR 任務: analyze_resume_async, ID: {job_id}...")
    
    try:
        # 使用 send_task
        result = app.send_task('analyze_resume_async', kwargs={'file_path': test_file, 'job_id': job_id})
        print(f"  - 任務已成功發送。")
        
        # 輪詢 Redis 中的 Job 狀態
        print(f"⏳ 開始輪詢 Redis 狀態 (f'job:{job_id}')...")
        max_polls = 10
        for i in range(max_polls):
            job_data = redis_client.hgetall(f"job:{job_id}")
            if job_data:
                status = job_data.get('status')
                print(f"  [Poll {i+1}] Status: {status}")
                
                if status == 'done':
                    print("✅ 任務成功完成！")
                    mapped_result = json.loads(job_data.get('result'))
                    print(f"📦 映射後的資料範例 (Name): {mapped_result.get('name')}")
                    return
                elif status == 'failed':
                    print(f"❌ 任務失敗: {job_data.get('error')}")
                    return
            else:
                print(f"  [Poll {i+1}] 尚未在 Redis 中找到 Job 資訊...")
                
            time.sleep(2)
        
        print("⏰ 輪詢超時。")
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")

if __name__ == "__main__":
    test_ocr_async()
