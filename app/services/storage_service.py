import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def upload_files(files_to_upload: dict) -> dict:
    if not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_JSON):
        logger.warning("Google Service Account JSON not found! Skipping storage upload.")
        return {
            "video_url": f"file://{files_to_upload.get('video_path')}",
            "pdf_url": f"file://{files_to_upload.get('pdf_path')}",
            "doc_url": f"file://{files_to_upload.get('doc_path')}"
        }
    return {
        "video_url": f"http://127.0.0.1:8000/download?path={files_to_upload.get('video_path')}",
        "pdf_url": f"http://127.0.0.1:8000/download?path={files_to_upload.get('pdf_path')}",
        "doc_url": f"http://127.0.0.1:8000/download?path={files_to_upload.get('doc_path')}"
    }
