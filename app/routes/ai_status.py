from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/ai", tags=["status"])

# Redis connection has been temporarily commented out
# redis_conn = Redis.from_url(settings.UPSTASH_REDIS_URL.replace('redis://', 'rediss://') if 'upstash' in settings.UPSTASH_REDIS_URL else settings.UPSTASH_REDIS_URL)

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "processing_in_background",
        "message": "Redis is temporarily disabled. Please check your FastAPI terminal logs or the external callback for the final job status."
    }
