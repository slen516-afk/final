import sys
import os
import time
import uuid
from worker.celery_app import celery_app



def run_task_test(task_name, *args, **kwargs):
    """
    通用任務測試引擎
    :param task_name: 任務的全名 (字串)，例如 'worker.tasks.analyze_resume_async'
    :param args: 傳遞給任務的參數列表
    """
    print(f"\n{'='*60}")
    print(f"[Worker測試啟動] 任務名稱: {task_name}")
    print(f"{'='*60}")

    try:
        # 檢查celery連線
        celery_app.backend.client.ping() 
        print("--- Backend 連線測試成功 ---")
        
        # 1. 發送任務 (使用 send_task 避開循環匯入問題)
        print(f"正在發送任務至 Redis...")
        result = celery_app.send_task(task_name, args=args, kwargs=kwargs)
        print(f"任務 ID: {result.id}")

        # 2. 監控狀態
        last_state = None
        start_time = time.time()
        timeout = 120 # 先 120 秒

        while not result.ready():
            current_state = result.state
            if current_state != last_state:
                # 取得 meta 資料 (PROGRESS 狀態下的訊息)
                info = result.info if isinstance(result.info, dict) else {}
                msg = info.get('msg', '處理中...')
                print(f"狀態變更: [{current_state}] -> {msg}")
                last_state = current_state
            
            if time.time() - start_time > timeout:
                print("測試超時！")
                return
            time.sleep(2)

        # 3. 輸出最終結果
        if result.successful():
            print(f"✅ [測試成功] 執行結果: {result.result}")
        else:
            print(f"❌ [測試失敗] 狀態: {result.state}")
            print(f"⚠️ 錯誤內容: {result.result}")

    except Exception as e:
        print(f"測試執行異常: {e}")

if __name__ == "__main__":
    # 測試用ID
    test_user = f"user_{uuid.uuid4().hex[:4]}"
    
    # 簡易測試
    run_task_test('test_connection')