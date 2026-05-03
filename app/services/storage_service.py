import os
import cloudinary
import cloudinary.uploader
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME.strip(),
        api_key=settings.CLOUDINARY_API_KEY.strip(),
        api_secret=settings.CLOUDINARY_API_SECRET.strip(),
        secure=True
    )
elif settings.CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL.strip())

def upload_files(files_to_upload: dict) -> dict:
    results = {}
    
    if not settings.CLOUDINARY_URL and not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY):
        logger.warning("Cloudinary credentials not found!")
        return {
            "video_url": f"file://{files_to_upload.get('video_path')}",
            "pdf_url": f"file://{files_to_upload.get('pdf_path')}",
            "doc_url": f"file://{files_to_upload.get('doc_path')}",
            "pdf_thumbnail": ""
        }

    try:
        # 1. Upload Video
        video_path = files_to_upload.get("video_path")
        if video_path and os.path.exists(video_path):
            video_upload = cloudinary.uploader.upload(
                video_path, 
                resource_type="video",
                folder="tutorai/videos"
            )
            results["video_url"] = video_upload.get("secure_url")
        
        # 2. Upload PDF (As image to allow thumbnail generation)
        pdf_path = files_to_upload.get("pdf_path")
        if pdf_path and os.path.exists(pdf_path):
            logger.info(f"Uploading PDF as image for thumbnail: {pdf_path}")
            pdf_upload = cloudinary.uploader.upload(
                pdf_path, 
                resource_type="image",
                folder="tutorai/notes",
                format="pdf"
            )
            results["pdf_url"] = pdf_upload.get("secure_url")
            
            # Generate Thumbnail URL for the first page
            # We use Cloudinary transformations: pg_1 (page 1), w_500 (width), f_jpg (format)
            public_id = pdf_upload.get("public_id")
            results["pdf_thumbnail"] = cloudinary.utils.cloudinary_url(
                public_id,
                page=1,
                format="jpg",
                width=500,
                crop="scale"
            )[0]
            
        # 3. Upload DOCX (Keep as raw)
        doc_path = files_to_upload.get("doc_path")
        if doc_path and os.path.exists(doc_path):
            doc_upload = cloudinary.uploader.upload(
                doc_path, 
                resource_type="raw",
                folder="tutorai/notes"
            )
            results["doc_url"] = doc_upload.get("secure_url")
            
        return results
        
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}")
        return {
            "video_url": results.get("video_url") or f"file://{files_to_upload.get('video_path')}",
            "pdf_url": results.get("pdf_url") or f"file://{files_to_upload.get('pdf_path')}",
            "doc_url": results.get("doc_url") or f"file://{files_to_upload.get('doc_path')}",
            "pdf_thumbnail": ""
        }
