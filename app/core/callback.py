import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_callback(job_id: str, status: str, video_url: str = None, pdf_url: str = None, doc_url: str = None, pdf_thumbnail: str = None):
    url = settings.NODE_CALLBACK_URL
    secret = settings.INTERNAL_API_SECRET.strip()
    headers = {
        "Authorization": f"Bearer {secret}"
    }
    payload = {
        "job_id": job_id,
        "status": status,
        "video_url": video_url,
        "pdf_url": pdf_url,
        "doc_url": doc_url,
        "pdf_thumbnail": pdf_thumbnail
    }
    logger.info(f"Sending callback to {url} for job {job_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Callback sent successfully")
    except Exception as e:
        logger.error(f"Failed to send callback: {e}")
