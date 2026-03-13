from core.redis_client import redis_client
import json

job_id = "job_56c647a48a23"
data = redis_client.hgetall(f"job:{job_id}")
print(json.dumps({k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v for k, v in data.items()}, indent=2))
