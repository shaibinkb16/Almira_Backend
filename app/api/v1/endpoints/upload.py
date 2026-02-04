"""
File Upload endpoints.
Handles image and file uploads to Supabase Storage.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import List
import uuid
import os

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser, CurrentUserOptional
from app.schemas.common import APIResponse

router = APIRouter()

# Allowed file types
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

# Max file sizes (in bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Supabase Storage buckets
PRODUCTS_BUCKET = "products"
REVIEWS_BUCKET = "reviews"
SUPPORT_BUCKET = "support"
AVATARS_BUCKET = "avatars"


@router.post("/image", response_model=APIResponse)
async def upload_image(
    file: UploadFile = File(...),
    bucket: str = "reviews",  # products, reviews, support, avatars
    current_user: CurrentUserOptional = None,
):
    """
    Upload an image to Supabase Storage.
    Returns the public URL of the uploaded image.

    Buckets:
    - products: Product images (admin only)
    - reviews: Review images (authenticated users)
    - support: Support ticket attachments (all users)
    - avatars: User profile pictures (authenticated users)
    """
    try:
        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        # Read file content
        contents = await file.read()
        file_size = len(contents)

        # Validate file size
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024)}MB",
            )

        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Add user folder if authenticated
        if current_user:
            file_path = f"{current_user.id}/{unique_filename}"
        else:
            file_path = f"public/{unique_filename}"

        # Upload to Supabase Storage
        supabase = get_supabase_admin()

        # Upload file
        result = supabase.storage.from_(bucket).upload(
            file_path,
            contents,
            file_options={"content-type": file.content_type}
        )

        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(file_path)

        return APIResponse(
            success=True,
            message="Image uploaded successfully.",
            data={
                "url": public_url,
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": file_size,
                "content_type": file.content_type,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )


@router.post("/images/multiple", response_model=APIResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    bucket: str = "reviews",
    current_user: CurrentUserOptional = None,
):
    """
    Upload multiple images at once.
    Maximum 5 images per request.
    """
    try:
        if len(files) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 images allowed per upload.",
            )

        uploaded_urls = []

        for file in files:
            # Validate file type
            if file.content_type not in ALLOWED_IMAGE_TYPES:
                continue  # Skip invalid files

            # Read file
            contents = await file.read()
            file_size = len(contents)

            if file_size > MAX_IMAGE_SIZE:
                continue  # Skip large files

            # Generate filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"

            # Add user folder
            if current_user:
                file_path = f"{current_user.id}/{unique_filename}"
            else:
                file_path = f"public/{unique_filename}"

            # Upload
            supabase = get_supabase_admin()
            result = supabase.storage.from_(bucket).upload(
                file_path,
                contents,
                file_options={"content-type": file.content_type}
            )

            # Get URL
            public_url = supabase.storage.from_(bucket).get_public_url(file_path)

            uploaded_urls.append({
                "url": public_url,
                "filename": unique_filename,
                "original_filename": file.filename,
            })

        return APIResponse(
            success=True,
            message=f"{len(uploaded_urls)} images uploaded successfully.",
            data={"images": uploaded_urls},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload images.",
        )


@router.delete("/image", response_model=APIResponse)
async def delete_image(
    file_path: str,
    bucket: str = "reviews",
    current_user: CurrentUser = None,
):
    """
    Delete an image from storage.
    Users can only delete their own images.
    """
    try:
        # Verify user owns the file (if authenticated)
        if current_user and not file_path.startswith(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own files.",
            )

        supabase = get_supabase_admin()
        result = supabase.storage.from_(bucket).remove([file_path])

        return APIResponse(
            success=True,
            message="Image deleted successfully.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image.",
        )
