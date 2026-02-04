"""
Category endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_client
from app.schemas.category import CategoryResponse, CategoryTreeNode
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[list[CategoryResponse]])
async def list_categories():
    """
    List all active categories.
    """
    try:
        client = get_supabase_client()

        result = client.table("categories").select(
            "*, products(count)"
        ).eq("is_active", True).order("display_order").execute()

        categories = [
            CategoryResponse(
                id=c["id"],
                name=c["name"],
                slug=c["slug"],
                description=c.get("description"),
                image_url=c.get("image_url"),
                parent_id=c.get("parent_id"),
                is_active=c["is_active"],
                display_order=c["display_order"],
                product_count=c.get("products", [{}])[0].get("count", 0) if c.get("products") else 0,
                created_at=c["created_at"],
                updated_at=c["updated_at"],
            )
            for c in result.data
        ]

        return APIResponse(success=True, data=categories)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories.",
        )


@router.get("/tree", response_model=APIResponse[list[CategoryTreeNode]])
async def get_category_tree():
    """
    Get categories as a nested tree structure.
    """
    try:
        client = get_supabase_client()

        result = client.table("categories").select("*").eq("is_active", True).order("display_order").execute()

        # Build tree
        categories_by_id = {c["id"]: {**c, "children": []} for c in result.data}
        root_categories = []

        for cat in result.data:
            if cat["parent_id"] and cat["parent_id"] in categories_by_id:
                categories_by_id[cat["parent_id"]]["children"].append(categories_by_id[cat["id"]])
            else:
                root_categories.append(categories_by_id[cat["id"]])

        return APIResponse(success=True, data=root_categories)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category tree.",
        )


@router.get("/{slug}", response_model=APIResponse[CategoryResponse])
async def get_category(slug: str):
    """
    Get a category by slug.
    """
    try:
        client = get_supabase_client()

        result = client.table("categories").select("*").eq("slug", slug).eq("is_active", True).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        c = result.data
        return APIResponse(
            success=True,
            data=CategoryResponse(
                id=c["id"],
                name=c["name"],
                slug=c["slug"],
                description=c.get("description"),
                image_url=c.get("image_url"),
                parent_id=c.get("parent_id"),
                is_active=c["is_active"],
                display_order=c["display_order"],
                created_at=c["created_at"],
                updated_at=c["updated_at"],
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category.",
        )
