import os
import shutil
from app.services.rag_service import process_rag
from app.services.notes_service import generate_notes
from app.services.video_service import generate_video
from app.services.storage_service import upload_files

def main():
    print("=== Testing RAG Service ===")
    topic = "What is Mathematics?"
    try:
        rag_output = process_rag(topic=topic)
        print("RAG Output:", rag_output)
    except Exception as e:
        print("RAG Service Failed:", e)
        return

    output_dir = "./test_output_dir"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print("\n=== Testing Notes Service ===")
    try:
        notes_files = generate_notes(notes_data=rag_output, output_dir=output_dir)
        print("Notes Paths:", notes_files)
    except Exception as e:
        print("Notes Service Failed:", e)
        return

    print("\n=== Testing Video Service ===")
    try:
        video_files = generate_video(notes_data=rag_output, output_dir=output_dir)
        print("Video Paths:", video_files)
    except Exception as e:
        print("Video Service Failed:", e)
        return

    print("\n=== Testing Storage Service ===")
    try:
        files_to_upload = {**notes_files, **video_files}
        uploaded_urls = upload_files(files_to_upload=files_to_upload)
        print("Uploaded URLs:", uploaded_urls)
    except Exception as e:
        print("Storage Service Failed:", e)
        return

    print("\nAll Services Passed successfully!")

if __name__ == "__main__":
    main()
