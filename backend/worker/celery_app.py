# Celert 配置檔
# 初始化 Celery 並連結到 Redis
from celery import Celery

def make_celery(app_name):
    # redis://localhost:6379/0 分別代表 協議://主機:埠號/資料庫編號
    broker = 'redis://localhost:6379/0'
    backend = 'redis://localhost:6379/0'
    
    return Celery(
        app_name,
        broker=broker,
        backend=backend,
        include=['worker.tasks']  # 告訴 Worker 去哪裡找任務定義
    )

celery_app = make_celery('my_async_project')