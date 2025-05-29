import redis
from rq import Worker
from src.task_queue import task_queue

if __name__ == "__main__":
    redis_conn = task_queue.connection
    worker = Worker([task_queue], connection=redis_conn)
    worker.work()
