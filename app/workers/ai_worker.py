import asyncio
import os
import shutil
from app.services.rag_service import process_rag
from app.services.video_service import generate_video
from app.services.notes_service import generate_notes
from app.services.storage_service import upload_files
from app.core.callback import send_callback

def process_job_sync(job_id: str, topic: str = None, pdf_path: str = None):
    try:
        temp_dir = f"/tmp/{job_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"[{job_id}] Running RAG Pipeline...")
        notes_data = process_rag(topic=topic, pdf_path=pdf_path)
        
        print(f"[{job_id}] Generating Video...")
        video_data = generate_video(notes_data, temp_dir)
        
        print(f"[{job_id}] Generating Notes...")
        docs_data = generate_notes(notes_data, temp_dir)
        
        print(f"[{job_id}] Uploading Files...")
        files_to_upload = {
            "video_path": video_data.get("video_path"),
            "pdf_path": docs_data.get("pdf_path"),
            "doc_path": docs_data.get("doc_path")
        }
        upload_urls = upload_files(files_to_upload)
        
        print(f"[{job_id}] Sending Callback...")
        asyncio.run(send_callback(
            job_id=job_id,
            status="completed",
            video_url=upload_urls.get("video_url"),
            pdf_url=upload_urls.get("pdf_url"),
            doc_url=upload_urls.get("doc_url"),
            pdf_thumbnail=upload_urls.get("pdf_thumbnail")
        ))
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)
            
    except Exception as e:
        print(f"[{job_id}] Error: {str(e)}")
        asyncio.run(send_callback(
            job_id=job_id,
            status="failed"
        ))
