import os
import redis
from rq import Queue

# Redis connection (host matches docker-compose service name)
redis_host = os.environ.get(
    "REDIS_HOST", "redis" if os.environ.get("DOCKER_COMPOSE") else "localhost"
)
redis_conn = redis.Redis(host=redis_host, port=6379, db=0)

# Default queue
task_queue = Queue("default", connection=redis_conn)
