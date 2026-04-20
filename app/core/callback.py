import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_callback(job_id: str, status: str, video_url: str = None, pdf_url: str = None, doc_url: str = None):
    url = "http://localhost:3000/api/ai/callback" # Replace with actual external API URL
    headers = {
        "Authorization": f"Bearer {settings.INTERNAL_API_SECRET}"
    }
    payload = {
        "job_id": job_id,
        "status": status,
        "video_url": video_url,
        "pdf_url": pdf_url,
        "doc_url": doc_url
    }
    logger.info(f"Sending callback for job {job_id} with status {status}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Callback sent successfully")
    except Exception as e:
        logger.error(f"Failed to send callback: {e}")
