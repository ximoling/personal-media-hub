from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.models import User, File as FileModel
from app.utils.image_processor import process_image

router = APIRouter(prefix="/api/files", tags=["files"])


class FileResponseModel(BaseModel):
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    thumb_path: Optional[str] = None
    file_path: str
    category_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


def convert_file_path(file_obj):
    """转换文件路径为URL格式"""
    result = {
        'id': file_obj.id,
        'filename': file_obj.filename,
        'original_name': file_obj.original_name,
        'file_type': file_obj.file_type,
        'file_size': file_obj.file_size,
        'mime_type': file_obj.mime_type,
        'width': file_obj.width,
        'height': file_obj.height,
        'category_id': file_obj.category_id,
        'created_at': file_obj.created_at,
    }
    
    if file_obj.file_path:
        basename = os.path.basename(file_obj.file_path)
        result['file_path'] = f"/uploads/{basename}"
    else:
        result['file_path'] = ""
    
    if file_obj.thumb_path:
        thumb_basename = os.path.basename(file_obj.thumb_path)
        result['thumb_path'] = f"/thumbs/{thumb_basename}"
    else:
        result['thumb_path'] = None
    
    return result


class FileListResponse(BaseModel):
    items: List[FileResponseModel]
    total: int


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    ext = get_file_extension(original_filename or "bin")
    return f"{uuid.uuid4().hex}{ext}"


def get_file_type(mime_type: str) -> str:
    if mime_type and mime_type.startswith("image/"):
        return "image"
    elif mime_type and mime_type.startswith("video/"):
        return "video"
    else:
        return "document"


EXTENSION_MIME_MAP = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml',
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.avi': 'video/x-msvideo',
    '.mkv': 'video/x-matroska',
    '.webm': 'video/webm',
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed',
}


def is_allowed_file(content_type: str, filename: str = "") -> bool:
    ext = get_file_extension(filename)
    mapped_type = EXTENSION_MIME_MAP.get(ext)
    
    check_type = content_type or mapped_type
    
    if check_type == 'video/mp4' or ext == '.mp4':
        return True
    if check_type == 'video/quicktime' or ext == '.mov':
        return True
    if ext in ['.avi', '.mkv', '.webm']:
        return True
    
    if check_type in settings.ALLOWED_IMAGE_TYPES or (mapped_type and mapped_type in settings.ALLOWED_IMAGE_TYPES):
        return True
    if check_type in settings.ALLOWED_VIDEO_TYPES or (mapped_type and mapped_type in settings.ALLOWED_VIDEO_TYPES):
        return True
    if check_type in settings.ALLOWED_DOCUMENT_TYPES or (mapped_type and mapped_type in settings.ALLOWED_DOCUMENT_TYPES):
        return True
    
    return False


@router.post("/upload", response_model=FileResponseModel)
async def upload_file(
    file: UploadFile = File(...),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传文件"""
    if not is_allowed_file(file.content_type, file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type or 'unknown'} not allowed"
        )

    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )

    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(file_content)

    thumb_path = None
    width = None
    height = None

    if file.content_type and file.content_type.startswith("image/"):
        try:
            thumb_path, width, height = process_image(file_path, unique_filename)
        except Exception as e:
            print(f"Error processing image: {e}")
    elif file.content_type and file.content_type.startswith("video/"):
        thumb_path = None
        width = None
        height = None

    db_file = FileModel(
        filename=unique_filename,
        original_name=file.filename or "unknown",
        file_path=file_path,
        thumb_path=thumb_path,
        file_type=get_file_type(file.content_type),
        file_size=len(file_content),
        mime_type=file.content_type or "application/octet-stream",
        width=width,
        height=height,
        user_id=current_user.id,
        category_id=category_id
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return convert_file_path(db_file)


@router.get("/list", response_model=FileListResponse)
def list_files(
    category_id: Optional[int] = None,
    file_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件列表"""
    query = db.query(FileModel).filter(FileModel.user_id == current_user.id)

    if category_id:
        query = query.filter(FileModel.category_id == category_id)

    if file_type:
        query = query.filter(FileModel.file_type == file_type)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(FileModel.original_name.ilike(search_pattern))

    total = query.count()
    files = query.order_by(FileModel.created_at.desc()).offset(skip).limit(limit).all()

    converted_files = [convert_file_path(f) for f in files]
    return FileListResponse(items=converted_files, total=total)


@router.get("/types")
def get_file_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件类型统计"""
    from sqlalchemy import func

    results = db.query(
        FileModel.file_type,
        func.count(FileModel.id).label("count")
    ).filter(FileModel.user_id == current_user.id).group_by(FileModel.file_type).all()

    return {"types": [{"type": r.file_type, "count": r.count} for r in results]}


@router.get("/{file_id}", response_model=FileResponseModel)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文件详情"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return convert_file_path(file)


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除文件"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    try:
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        if file.thumb_path and os.path.exists(file.thumb_path):
            os.remove(file.thumb_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.delete(file)
    db.commit()

    return {"message": "File deleted successfully"}


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载文件"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    return FastAPIFileResponse(
        path=file.file_path,
        filename=file.original_name,
        media_type=file.mime_type
    )


@router.get("/{file_id}/preview")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """预览文件"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    return FastAPIFileResponse(
        path=file.file_path,
        media_type=file.mime_type
    )
