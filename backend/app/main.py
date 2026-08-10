from fastapi import FastAPI

app = FastAPI(title="AI Code Reviewer")

@app.get("/")
def root():
    return {"message": "AI Code Reviewer API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
