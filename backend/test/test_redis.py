import redis
import os

REDIS_URL = os.getenv('REDIS_URL', 'redis://final-redis:6379/0')

try:
    r = redis.from_url(REDIS_URL)
    if r.ping():
        print("✅ [Checkpoints] Redis 啟動正常且連線成功！")
except Exception as e:
    print(f"❌ [Checkpoints] Redis 連線失敗。錯誤訊息: {e}")