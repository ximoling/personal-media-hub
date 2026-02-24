from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.api import auth, files, categories
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Create necessary directories
from app.core.config import settings
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.THUMB_DIR, exist_ok=True)

app = FastAPI(
    title="Personal Media Hub",
    description="A personal media management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(categories.router)

# Serve static files (thumbnails and uploads)
app.mount("/thumbs", StaticFiles(directory=settings.THUMB_DIR), name="thumbnails")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/")
def root():
    """Serve the frontend HTML"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        with open(frontend_file, "r", encoding="utf-8") as f:
            content = f.read()
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=content)
    return {
        "message": "Personal Media Hub API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}