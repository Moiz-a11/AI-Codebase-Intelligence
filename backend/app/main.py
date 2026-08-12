from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router

app = FastAPI(
    title="AI Codebase Intelligence",
    description="AI-powered codebase analysis using RAG",
    version="1.0.0",
)

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)


@app.get("/")
def root():
    return {
        "message": "AI Codebase Intelligence API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }