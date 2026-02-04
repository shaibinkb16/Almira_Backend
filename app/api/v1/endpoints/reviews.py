"""
Product review endpoints.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.supabase import get_supabase_client, get_supabase_admin
from app.middleware.auth import CurrentUser, CurrentUserOptional
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewSummary
from app.schemas.common import APIResponse, PaginatedResponse, create_pagination_meta

router = APIRouter()


@router.get("/product/{product_id}", response_model=PaginatedResponse[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    rating: Optional[int] = Query(None, ge=1, le=5),
):
    """
    Get reviews for a product.
    """
    try:
        client = get_supabase_client()

        query = client.table("reviews").select(
            "*, profiles(full_name, avatar_url)", count="exact"
        ).eq("product_id", product_id).eq("status", "approved")

        if rating:
            query = query.eq("rating", rating)

        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        reviews = [
            ReviewResponse(
                id=r["id"],
                product_id=r["product_id"],
                user_id=r["user_id"],
                user_name=r.get("profiles", {}).get("full_name", "Anonymous"),
                user_avatar=r.get("profiles", {}).get("avatar_url"),
                rating=r["rating"],
                title=r.get("title"),
                comment=r.get("comment"),
                images=r.get("images", []),
                status=r["status"],
                is_verified_purchase=r.get("is_verified_purchase", False),
                helpful_count=r.get("helpful_count", 0),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in result.data
        ]

        return PaginatedResponse(
            data=reviews,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews.",
        )


@router.get("/product/{product_id}/summary", response_model=APIResponse[ReviewSummary])
async def get_review_summary(product_id: str):
    """
    Get review summary for a product.
    """
    try:
        client = get_supabase_client()

        result = client.table("reviews").select("rating").eq(
            "product_id", product_id
        ).eq("status", "approved").execute()

        ratings = [r["rating"] for r in result.data]
        total = len(ratings)
        avg = sum(ratings) / total if total > 0 else 0

        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in ratings:
            distribution[r] += 1

        return APIResponse(
            success=True,
            data=ReviewSummary(
                product_id=product_id,
                average_rating=round(avg, 2),
                total_reviews=total,
                rating_distribution=distribution,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch review summary.",
        )


@router.post("", response_model=APIResponse[ReviewResponse])
async def create_review(review_data: ReviewCreate, current_user: CurrentUser):
    """
    Create a product review.
    """
    try:
        admin = get_supabase_admin()

        # Check if user already reviewed this product
        existing = admin.table("reviews").select("id").eq(
            "product_id", review_data.product_id
        ).eq("user_id", current_user.id).execute()

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this product.",
            )

        # Check if user purchased the product
        purchase = admin.table("order_items").select("id").eq(
            "product_id", review_data.product_id
        ).execute()

        is_verified = len(purchase.data) > 0 if purchase.data else False

        # Create review
        result = admin.table("reviews").insert({
            "product_id": review_data.product_id,
            "user_id": current_user.id,
            "rating": review_data.rating,
            "title": review_data.title,
            "comment": review_data.comment,
            "images": review_data.images,
            "is_verified_purchase": is_verified,
            "status": "pending",  # Reviews need moderation
        }).execute()

        r = result.data[0]

        return APIResponse(
            success=True,
            message="Review submitted for moderation.",
            data=ReviewResponse(
                id=r["id"],
                product_id=r["product_id"],
                user_id=r["user_id"],
                user_name=current_user.full_name or "Anonymous",
                rating=r["rating"],
                title=r.get("title"),
                comment=r.get("comment"),
                images=r.get("images", []),
                status=r["status"],
                is_verified_purchase=r["is_verified_purchase"],
                helpful_count=0,
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review.",
        )
