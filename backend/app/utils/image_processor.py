from PIL import Image, ExifTags
import os
from pathlib import Path
from app.core.config import settings

def process_image(file_path: str, filename: str, thumb_size: tuple = (300, 300)):
    """处理图片，生成缩略图，读取EXIF信息"""
    try:
        # Open image
        with Image.open(file_path) as img:
            # Get original dimensions
            width, height = img.size
            
            # Handle EXIF orientation
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation)
                    if orientation_value == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation_value == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation_value == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                pass
            
            # Generate thumbnail
            thumb_dir = Path(settings.THUMB_DIR)
            thumb_dir.mkdir(parents=True, exist_ok=True)
            
            thumb_filename = f"thumb_{filename}"
            thumb_path = thumb_dir / thumb_filename
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(thumb_path, "JPEG", quality=85)
            
            return str(thumb_path), width, height
            
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        return None, None, None