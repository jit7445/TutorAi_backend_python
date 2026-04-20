import os
import shutil
from app.services.rag_service import process_rag
from app.services.video_service import generate_video
from app.services.notes_service import generate_notes
from app.services.storage_service import upload_files

def test_all_services():
    test_id = "test_unit_debug"
    temp_dir = f"./{test_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    print("\n[1/4] === TESTING RAG SERVICE ===")
    try:
        notes_data = process_rag(topic="Black Holes")
        print("✅ SUCCESS! Generated notes:")
        print(notes_data)
    except Exception as e:
        print("❌ RAG SERVICE FAILED:")
        import traceback
        traceback.print_exc()
        return

    print("\n[2/4] === TESTING VIDEO SERVICE ===")
    try:
        video_data = generate_video(notes_data, temp_dir)
        print(f"✅ SUCCESS! Generated video at: {video_data}")
    except Exception as e:
        print("❌ VIDEO SERVICE FAILED:")
        import traceback
        traceback.print_exc()
        return
        
    print("\n[3/4] === TESTING NOTES SERVICE ===")
    try:
        docs_data = generate_notes(notes_data, temp_dir)
        print(f"✅ SUCCESS! Generated documents at: {docs_data}")
    except Exception as e:
        print("❌ NOTES SERVICE FAILED:")
        import traceback
        traceback.print_exc()
        return
        
    print("\n[4/4] === TESTING STORAGE SERVICE ===")
    try:
        files_to_upload = {
            "video_path": video_data.get("video_path"),
            "pdf_path": docs_data.get("pdf_path"),
            "doc_path": docs_data.get("doc_path")
        }
        upload_urls = upload_files(files_to_upload)
        print(f"✅ SUCCESS! Upload URLs: {upload_urls}")
    except Exception as e:
        print("❌ STORAGE SERVICE FAILED:")
        import traceback
        traceback.print_exc()
        return
        
    print("\n🎉 ALL SERVICES RAN PERFECTLY!")
    
    # Clean up test files
    # shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\n📂 You can view your generated files here: {temp_dir}")

if __name__ == "__main__":
    test_all_services()
