"""
User profile endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.schemas.user import UserResponse, ProfileUpdate
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_current_user_profile(current_user: CurrentUser):
    """
    Get the current user's profile.
    """
    return APIResponse(
        success=True,
        data=UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            phone=current_user.phone,
            role=current_user.role,
            created_at=current_user.created_at,
        ),
    )


@router.patch("/me", response_model=APIResponse[UserResponse])
async def update_current_user_profile(
    profile_data: ProfileUpdate,
    current_user: CurrentUser,
):
    """
    Update the current user's profile.
    """
    try:
        admin = get_supabase_admin()

        # Build update data (only include non-None values)
        update_data = profile_data.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )

        # Update profile
        result = admin.table("profiles").update(update_data).eq("id", current_user.id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found.",
            )

        updated = result.data[0]

        return APIResponse(
            success=True,
            message="Profile updated successfully.",
            data=UserResponse(
                id=updated["id"],
                email=current_user.email,
                full_name=updated.get("full_name"),
                avatar_url=updated.get("avatar_url"),
                phone=updated.get("phone"),
                role=updated.get("role", "customer"),
                created_at=updated.get("created_at"),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile.",
        )


@router.delete("/me")
async def delete_current_user(current_user: CurrentUser):
    """
    Delete the current user's account.

    This is a soft delete - marks the account as inactive.
    """
    try:
        admin = get_supabase_admin()

        # Soft delete - mark as inactive
        admin.table("profiles").update({"is_active": False}).eq("id", current_user.id).execute()

        return APIResponse(
            success=True,
            message="Account deactivated successfully.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account.",
        )
