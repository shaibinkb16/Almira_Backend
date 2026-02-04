"""
Wishlist endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.schemas.product import ProductListResponse
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[list[ProductListResponse]])
async def get_wishlist(current_user: CurrentUser):
    """
    Get current user's wishlist.
    """
    try:
        admin = get_supabase_admin()

        result = admin.table("wishlist_items").select(
            "*, products(*)"
        ).eq("user_id", current_user.id).order("created_at", desc=True).execute()

        items = [
            ProductListResponse(
                id=w["products"]["id"],
                name=w["products"]["name"],
                slug=w["products"]["slug"],
                base_price=w["products"]["base_price"],
                sale_price=w["products"].get("sale_price"),
                status=w["products"]["status"],
                images=w["products"].get("images", []),
                rating=w["products"].get("rating", 0),
                review_count=w["products"].get("review_count", 0),
            )
            for w in result.data if w.get("products")
        ]

        return APIResponse(success=True, data=items)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wishlist.",
        )


@router.post("/{product_id}", response_model=APIResponse)
async def add_to_wishlist(product_id: str, current_user: CurrentUser):
    """
    Add product to wishlist.
    """
    try:
        admin = get_supabase_admin()

        # Check if already in wishlist
        existing = admin.table("wishlist_items").select("id").eq(
            "user_id", current_user.id
        ).eq("product_id", product_id).execute()

        if existing.data:
            return APIResponse(success=True, message="Product already in wishlist.")

        # Add to wishlist
        admin.table("wishlist_items").insert({
            "user_id": current_user.id,
            "product_id": product_id,
        }).execute()

        return APIResponse(success=True, message="Added to wishlist.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to wishlist.",
        )


@router.delete("/{product_id}", response_model=APIResponse)
async def remove_from_wishlist(product_id: str, current_user: CurrentUser):
    """
    Remove product from wishlist.
    """
    try:
        admin = get_supabase_admin()

        admin.table("wishlist_items").delete().eq(
            "user_id", current_user.id
        ).eq("product_id", product_id).execute()

        return APIResponse(success=True, message="Removed from wishlist.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove from wishlist.",
        )


@router.get("/check/{product_id}", response_model=APIResponse[bool])
async def check_in_wishlist(product_id: str, current_user: CurrentUser):
    """
    Check if product is in wishlist.
    """
    try:
        admin = get_supabase_admin()

        result = admin.table("wishlist_items").select("id").eq(
            "user_id", current_user.id
        ).eq("product_id", product_id).execute()

        return APIResponse(success=True, data=len(result.data) > 0)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check wishlist.",
        )
