from fastapi import FastAPI
from app.routes import ai_jobs, ai_status
from app.core.config import settings

app = FastAPI(title="Tutor AI Backend API")

app.include_router(ai_jobs.router)
app.include_router(ai_status.router)

@app.get("/")
def root():
    return {"message": "Welcome to Tutor AI Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.FASTAPI_PORT, reload=True)
