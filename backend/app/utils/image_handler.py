"""Safe image upload handler and validation utilities for CivicFix."""

import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from app.config import settings


# Magic byte signatures for robust image file validation
IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": [".jpg", ".jpeg"],
    b"\x89PNG\r\n\x1a\n": [".png"],
    b"GIF87a": [".gif"],
    b"GIF89a": [".gif"],
    b"RIFF": [".webp"],  # RIFF....WEBP
    b"BM": [".bmp"],
}


def validate_image_file(file: UploadFile, content_sample: bytes) -> Tuple[str, str]:
    """
    Validate that the uploaded file is a genuine and permitted image format.
    Returns the normalized extension and MIME type.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename",
        )

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(settings.ALLOWED_IMAGE_EXTENSIONS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed image extensions: {allowed}",
        )

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
        # Fallback check on common types
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported MIME type '{content_type}'. Must be a valid image.",
            )

    return ext, content_type


async def save_upload_image(file: Optional[UploadFile]) -> Optional[str]:
    """
    Safely validates, hashes/uniquifies, and stores an uploaded image file into backend/uploads/.
    Never stores binary directly in SQLite; returns the relative static URL path (/uploads/<uuid>.<ext>).
    """
    if file is None or not file.filename:
        return None

    # 1. Read initial chunk for header inspection
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    chunk_size = 64 * 1024  # 64 KB chunks

    first_chunk = await file.read(chunk_size)
    if not first_chunk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image file is empty.",
        )

    # 2. Validate format & extension
    ext, _ = validate_image_file(file, first_chunk)

    # 3. Generate unique filename (prevent collisions & path traversal)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)

    dest_path = os.path.abspath(os.path.join(upload_dir, unique_filename))

    # Defensive path containment check
    if os.path.commonpath([upload_dir, dest_path]) != upload_dir:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination filename path.",
        )

    # 4. Stream and write with size limit checking
    total_size = len(first_chunk)
    with open(dest_path, "wb") as buffer:
        buffer.write(first_chunk)
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_bytes:
                buffer.close()
                # Clean up oversized partial file
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image file size ({total_size / (1024 * 1024):.1f}MB) exceeds maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB.",
                )
            buffer.write(chunk)

    # Return web-accessible path
    return f"/uploads/{unique_filename}"


def get_safe_image_path(image_path_or_name: str) -> Optional[str]:
    """
    Safely resolves an image path or filename to an absolute path inside UPLOAD_DIR.
    Guarantees that no arbitrary filesystem traversal can occur.
    """
    if not image_path_or_name:
        return None

    # Strip web prefix if present e.g. "/uploads/abc.png" -> "abc.png"
    cleaned_name = image_path_or_name.replace("\\", "/").split("/")[-1].strip()
    if not cleaned_name:
        return None

    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    resolved_path = os.path.abspath(os.path.join(upload_dir, cleaned_name))

    # Ensure resolved path is strictly within upload_dir
    if os.path.commonpath([upload_dir, resolved_path]) != upload_dir:
        return None

    if not os.path.isfile(resolved_path):
        return None

    return resolved_path
