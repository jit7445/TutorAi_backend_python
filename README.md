# Tutor AI Backend

Tutor AI Backend is a powerful FastAPI-based application designed to automate the creation of educational content. It leverages advanced AI models and media generation libraries to transform topics or PDF documents into structured notes, downloadable documents (PDF/DOCX), and engaging educational videos.

## 🚀 Features

- **RAG (Retrieval-Augmented Generation) Pipeline**: Process complex topics or PDF documents using LangChain and ChromaDB to extract and structure educational content.
- **Automated Video Generation**: Create educational videos automatically using MoviePy, combining generated text, speech (gTTS), and visual elements.
- **Document Generation**: Automatically generate formatted study notes in both PDF (ReportLab) and DOCX (python-docx) formats.
- **Asynchronous Processing**: Uses FastAPI Background Tasks for efficient, non-blocking job execution.
- **Cloud Storage Integration**: Seamlessly uploads generated content to Google Drive.
- **Callback System**: Notifies external services upon job completion or failure.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI/LLM**: [LangChain](https://www.langchain.com/), OpenAI GPT, Google Gemini, HuggingFace
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Media Processing**: [MoviePy](https://zulko.github.io/moviepy/), [gTTS](https://gtts.readthedocs.io/), [Pillow](https://python-pillow.org/)
- **Document Processing**: [ReportLab](https://www.reportlab.com/), [python-docx](https://python-docx.readthedocs.io/), [PyPDF](https://pypdf.readthedocs.io/)
- **Storage**: Google Drive API

## 📋 Prerequisites

- Python 3.9+
- Redis (Optional, if using RQ worker)
- Google Cloud Service Account with Google Drive API enabled

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd tutorAi_backend_fastapi
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following:
   ```env
   FASTAPI_PORT=8000
   INTERNAL_API_SECRET=your_secret_key
   UPSTASH_REDIS_URL=redis://localhost:6379
   GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
   GDRIVE_ROOT_FOLDER_ID=your_google_drive_folder_id
   gpt_api_key=your_openai_api_key
   Gemini_api_key=your_gemini_api_key
   ```

5. **Google Cloud Setup**:
   Place your `service_account.json` file in the root directory.

## 🏃 Running the Application

To start the FastAPI server:
```bash
python app/main.py
```
The API will be available at `http://localhost:8000`. You can access the interactive documentation at `http://localhost:8000/docs`.

## 📂 Project Structure

```text
├── app/
│   ├── core/           # Configuration, constants, and utilities
│   ├── routes/         # API endpoint definitions (Jobs, Status)
│   ├── services/       # Business logic (RAG, Video, Notes, Storage)
│   ├── workers/        # Background job processing logic
│   └── main.py         # Application entry point
├── check_failed_job.py # Utility script for debugging
├── run_worker.py       # Script to run background workers
├── requirements.txt    # Project dependencies
└── service_account.json # Google Cloud credentials
```

## 📡 API Endpoints

### Create a Job
- **URL**: `/ai/jobs`
- **Method**: `POST`
- **Body** (Form-Data):
  - `topic` (Optional string): The educational topic to generate content for.
  - `file` (Optional PDF): A PDF document to use as source material.
- **Response**:
  ```json
  {
    "job_id": "uuid-string",
    "message": "Job queued successfully"
  }
  ```


