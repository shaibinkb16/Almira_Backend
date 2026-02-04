"""
Address management endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[list[AddressResponse]])
async def list_addresses(current_user: CurrentUser):
    """
    Get all addresses for current user.
    """
    try:
        admin = get_supabase_admin()

        result = admin.table("addresses").select("*").eq(
            "user_id", current_user.id
        ).order("is_default", desc=True).order("created_at", desc=True).execute()

        addresses = [AddressResponse(**a) for a in result.data]

        return APIResponse(success=True, data=addresses)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch addresses.",
        )


@router.post("", response_model=APIResponse[AddressResponse])
async def create_address(address_data: AddressCreate, current_user: CurrentUser):
    """
    Create a new address.
    """
    try:
        admin = get_supabase_admin()

        # If this is set as default, unset other defaults
        if address_data.is_default:
            admin.table("addresses").update({"is_default": False}).eq(
                "user_id", current_user.id
            ).execute()

        # Create address
        result = admin.table("addresses").insert({
            "user_id": current_user.id,
            **address_data.model_dump(),
        }).execute()

        return APIResponse(
            success=True,
            message="Address added successfully.",
            data=AddressResponse(**result.data[0]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create address.",
        )


@router.get("/{address_id}", response_model=APIResponse[AddressResponse])
async def get_address(address_id: str, current_user: CurrentUser):
    """
    Get a specific address.
    """
    try:
        admin = get_supabase_admin()

        result = admin.table("addresses").select("*").eq(
            "id", address_id
        ).eq("user_id", current_user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found.",
            )

        return APIResponse(success=True, data=AddressResponse(**result.data))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch address.",
        )


@router.patch("/{address_id}", response_model=APIResponse[AddressResponse])
async def update_address(
    address_id: str,
    address_data: AddressUpdate,
    current_user: CurrentUser,
):
    """
    Update an address.
    """
    try:
        admin = get_supabase_admin()

        update_data = address_data.model_dump(exclude_none=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )

        # If setting as default, unset others
        if update_data.get("is_default"):
            admin.table("addresses").update({"is_default": False}).eq(
                "user_id", current_user.id
            ).neq("id", address_id).execute()

        result = admin.table("addresses").update(update_data).eq(
            "id", address_id
        ).eq("user_id", current_user.id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found.",
            )

        return APIResponse(
            success=True,
            message="Address updated.",
            data=AddressResponse(**result.data[0]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update address.",
        )


@router.delete("/{address_id}", response_model=APIResponse)
async def delete_address(address_id: str, current_user: CurrentUser):
    """
    Delete an address.
    """
    try:
        admin = get_supabase_admin()

        admin.table("addresses").delete().eq(
            "id", address_id
        ).eq("user_id", current_user.id).execute()

        return APIResponse(success=True, message="Address deleted.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete address.",
        )


@router.post("/{address_id}/default", response_model=APIResponse)
async def set_default_address(address_id: str, current_user: CurrentUser):
    """
    Set an address as default.
    """
    try:
        admin = get_supabase_admin()

        # Unset all defaults
        admin.table("addresses").update({"is_default": False}).eq(
            "user_id", current_user.id
        ).execute()

        # Set this as default
        result = admin.table("addresses").update({"is_default": True}).eq(
            "id", address_id
        ).eq("user_id", current_user.id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found.",
            )

        return APIResponse(success=True, message="Default address updated.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set default address.",
        )
