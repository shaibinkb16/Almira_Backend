"""
Product endpoints.
Public product catalog with filtering and search.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.supabase import get_supabase_client
from app.schemas.product import ProductResponse, ProductListResponse, ProductFilter
from app.schemas.common import APIResponse, PaginatedResponse, create_pagination_meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProductListResponse])
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|price|name|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    in_stock: Optional[bool] = None,
    material: Optional[str] = None,
):
    """
    List products with filtering and pagination.

    - Supports category, price range, search, and stock filters
    - Sortable by date, price, name, or rating
    """
    try:
        client = get_supabase_client()

        # Start query
        query = client.table("products").select("*", count="exact")

        # Only active products
        query = query.eq("status", "active")

        # Apply filters
        if category_id:
            query = query.eq("category_id", category_id)

        if min_price is not None:
            query = query.gte("base_price", min_price)

        if max_price is not None:
            query = query.lte("base_price", max_price)

        if in_stock:
            query = query.gt("stock_quantity", 0)

        if material:
            query = query.eq("material", material)

        if search:
            query = query.ilike("name", f"%{search}%")

        # Sorting
        sort_column = "base_price" if sort_by == "price" else sort_by
        query = query.order(sort_column, desc=(sort_order == "desc"))

        # Pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        # Execute
        result = query.execute()

        # Transform to response
        products = [
            ProductListResponse(
                id=p["id"],
                name=p["name"],
                slug=p["slug"],
                base_price=p["base_price"],
                sale_price=p.get("sale_price"),
                status=p["status"],
                images=p.get("images", []),
                rating=p.get("rating", 0),
                review_count=p.get("review_count", 0),
            )
            for p in result.data
        ]

        return PaginatedResponse(
            data=products,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products.",
        )


@router.get("/{slug}", response_model=APIResponse[ProductResponse])
async def get_product(slug: str):
    """
    Get a single product by slug.

    Returns full product details including variants.
    """
    try:
        client = get_supabase_client()

        # Get product
        result = client.table("products").select(
            "*, categories(name)"
        ).eq("slug", slug).eq("status", "active").single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        product = result.data

        # Get variants
        variants_result = client.table("product_variants").select("*").eq(
            "product_id", product["id"]
        ).eq("is_active", True).execute()

        return APIResponse(
            success=True,
            data=ProductResponse(
                id=product["id"],
                name=product["name"],
                slug=product["slug"],
                description=product.get("description"),
                short_description=product.get("short_description"),
                base_price=product["base_price"],
                sale_price=product.get("sale_price"),
                sku=product["sku"],
                stock_quantity=product["stock_quantity"],
                category_id=product.get("category_id"),
                category_name=product.get("categories", {}).get("name") if product.get("categories") else None,
                status=product["status"],
                images=product.get("images", []),
                variants=variants_result.data or [],
                tags=product.get("tags", []),
                material=product.get("material"),
                purity=product.get("purity"),
                weight=product.get("weight"),
                gemstones=product.get("gemstones"),
                rating=product.get("rating", 0),
                review_count=product.get("review_count", 0),
                created_at=product["created_at"],
                updated_at=product["updated_at"],
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product.",
        )


@router.get("/{product_id}/related", response_model=APIResponse[list[ProductListResponse]])
async def get_related_products(product_id: str, limit: int = Query(4, ge=1, le=12)):
    """
    Get related products based on category.
    """
    try:
        client = get_supabase_client()

        # Get current product's category
        product = client.table("products").select("category_id").eq("id", product_id).single().execute()

        if not product.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        # Get related products from same category
        result = client.table("products").select("*").eq(
            "category_id", product.data["category_id"]
        ).neq("id", product_id).eq("status", "active").limit(limit).execute()

        products = [
            ProductListResponse(
                id=p["id"],
                name=p["name"],
                slug=p["slug"],
                base_price=p["base_price"],
                sale_price=p.get("sale_price"),
                status=p["status"],
                images=p.get("images", []),
                rating=p.get("rating", 0),
                review_count=p.get("review_count", 0),
            )
            for p in result.data
        ]

        return APIResponse(success=True, data=products)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch related products.",
        )
