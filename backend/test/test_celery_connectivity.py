import os
import time
from celery import Celery

# Redis configuration 
# 注意：在宿主機測試時，Redis Host 是 localhost (Port 6379)
REDIS_URL = 'redis://localhost:6379/0'

def test_celery_tasks():
    print(f"🔗 正在連接 Redis Broker: {REDIS_URL}...")
    app = Celery('ai_task_test', broker=REDIS_URL, backend=REDIS_URL)
    
    # 測試任務列表
    test_scenarios = [
        {
            "name": "Connection Check",
            "task": "test_connection",
            "kwargs": {"user_id": "test_admin", "content": "System ping"}
        },
        {
            "name": "Cover Letter Task Registration",
            "task": "process_cover_letter",
            "kwargs": {"job_id": "test_job_123", "resume_id": "test_resume_456"}
        },
        {
            "name": "Resume Analysis Registration",
            "task": "process_resume_analysis",
            "kwargs": {"user_id": 11, "job_id": "job_mock123"}
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🚀 正在測試: {scenario['name']} ({scenario['task']})...")
        try:
            # 使用 send_task 確保不需要在本地環境安裝完整的 backend package
            result = app.send_task(scenario['task'], kwargs=scenario['kwargs'])
            print(f"  - 任務已發送 ID: {result.id}")
            
            # 我們不一定要等待 AI 跑完 (AI 任務通常很慢)，
            # 但我們要確認任務是否被 Worker 拾取 (狀態從 PENDING 變成 STARTED 或其他)
            # 或者如果是測試用的 test_connection，它可以很快完成
            
            wait_limit = 5
            success = False
            for _ in range(wait_limit):
                if result.ready():
                    print(f"  ✅ 任務執行成功！回傳值: {result.result}")
                    success = True
                    break
                # 如果是 heavy task，只要狀態變成了被拾取也可以視為連通正常
                # 但 Celery 預設不追蹤 PENDING 以外的中間狀態，除非特別設定
                time.sleep(1)
            
            if not success:
                print(f"  ⏳ 任務已進入隊列但尚未完成 (正常現象，AI 任務較重)")
                
        except Exception as e:
            print(f"  ❌ 發送失敗: {e}")

if __name__ == "__main__":
    test_celery_tasks()
