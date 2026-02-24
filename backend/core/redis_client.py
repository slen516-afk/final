import os
import redis

# ---------- Configuration ----------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

STREAM_NAME = "cv_jobs"
DLQ_STREAM_NAME = "cv_jobs_dlq"
GROUP_NAME = "cv_workers"

MAX_RETRY = 3


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)

redis_client: redis.Redis = get_redis_client()
