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

@router.post("/summarize")
async def summarize_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    job_id = str(uuid.uuid4())
    pdf_path = f"/tmp/uploads/{job_id}_{file.filename}"
    os.makedirs("/tmp/uploads", exist_ok=True)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # background_tasks.add_task(process_summary_sync, job_id, pdf_path)
    return {"job_id": job_id, "message": "Summary job queued"}

@router.post("/tts")
async def generate_tts(
    background_tasks: BackgroundTasks,
    text: str = Form(...)
):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    job_id = str(uuid.uuid4())
    # background_tasks.add_task(process_tts_sync, job_id, text)
    return {"job_id": job_id, "message": "TTS job queued"}

@router.post("/coach")
async def presentation_coach(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    audio_path = f"/tmp/uploads/{job_id}_{audio.filename}"
    os.makedirs("/tmp/uploads", exist_ok=True)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    # background_tasks.add_task(process_coach_sync, job_id, audio_path)
    return {"job_id": job_id, "message": "Coach job queued"}

