from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Personal Media Hub"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/database.db"
    
    # Storage
    UPLOAD_DIR: str = "./data/uploads"
    THUMB_DIR: str = "./data/thumbs"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Allowed file types
    ALLOWED_IMAGE_TYPES: list = [
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/heic", "image/heif",
        "image/tiff", "image/bmp", "image/svg+xml"
    ]
    ALLOWED_VIDEO_TYPES: list = [
        "video/mp4", "video/quicktime", "video/x-msvideo", "video/x-ms-wmv",
        "video/x-matroska", "video/webm", "video/3gpp", "video/3gpp2"
    ]
    ALLOWED_DOCUMENT_TYPES: list = [
        "application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain", "text/csv", "application/zip", "application/x-rar-compressed",
        "application/octet-stream"
    ]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()