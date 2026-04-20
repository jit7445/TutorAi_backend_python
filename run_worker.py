import os
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
from redis import Redis
from rq import Worker, Queue
from app.core.config import settings

# Automatically get the Upstash URL from your .env file
redis_url = settings.UPSTASH_REDIS_URL.replace('redis://', 'rediss://') if 'upstash' in settings.UPSTASH_REDIS_URL else settings.UPSTASH_REDIS_URL

listen = ['ai_jobs']
conn = Redis.from_url(redis_url)

if __name__ == '__main__':
    print(f"Starting worker... Connecting to: {redis_url.split('@')[-1]}")
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
