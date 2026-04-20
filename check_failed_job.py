import os
from redis import Redis
from rq.job import Job
from app.core.config import settings

redis_url = settings.UPSTASH_REDIS_URL.replace('redis://', 'rediss://') if 'upstash' in settings.UPSTASH_REDIS_URL else settings.UPSTASH_REDIS_URL
redis_conn = Redis.from_url(redis_url)

job_id = "0d4ab31d-8f2d-4d98-ae78-6f2502ba3683"
job = Job.fetch(job_id, connection=redis_conn)
print(job.exc_info)
