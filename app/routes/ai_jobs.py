import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.workers.ai_worker import process_job_sync
from app.core.config import settings
from typing import Optional

router = APIRouter(prefix="/ai", tags=["jobs"])

# Redis queue has been temporarily commented out for simplicity
# redis_conn = Redis.from_url(settings.UPSTASH_REDIS_URL.replace('redis://', 'rediss://') if 'upstash' in settings.UPSTASH_REDIS_URL else settings.UPSTASH_REDIS_URL)
# queue = Queue('ai_jobs', connection=redis_conn)

@router.post("/jobs")
async def create_job(
    background_tasks: BackgroundTasks,
    topic: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not topic and not file:
        raise HTTPException(status_code=400, detail="Must provide topic or file")

    job_id = str(uuid.uuid4())
    pdf_path = None
    
    if file:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        temp_dir = f"/tmp/uploads"
        os.makedirs(temp_dir, exist_ok=True)
        pdf_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    # Use FastAPI BackgroundTasks directly instead of RQ/Redis
    background_tasks.add_task(
        process_job_sync,
        job_id=job_id,
        topic=topic,
        pdf_path=pdf_path
    )
    
    return {"job_id": job_id, "message": "Job queued successfully using FastAPI Background Tasks"}
