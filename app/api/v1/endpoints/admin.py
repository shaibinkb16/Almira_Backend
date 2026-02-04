"""
Admin endpoints for managing the store.
All endpoints require admin role.
"""

from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentAdmin
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.order import OrderUpdate, OrderResponse
from app.schemas.review import ReviewModerate, ReviewResponse
from app.schemas.user import UserResponse
from app.schemas.common import APIResponse, PaginatedResponse, create_pagination_meta

router = APIRouter()


# ===========================================
# DASHBOARD
# ===========================================

@router.get("/dashboard")
async def get_dashboard_stats(admin: CurrentAdmin):
    """
    Get dashboard statistics.
    """
    try:
        db = get_supabase_admin()

        # Get counts
        products = db.table("products").select("id", count="exact").execute()
        orders = db.table("orders").select("id", count="exact").execute()
        users = db.table("profiles").select("id", count="exact").eq("role", "customer").execute()

        # Get revenue
        revenue = db.table("orders").select("total_amount").eq("payment_status", "paid").execute()
        total_revenue = sum(Decimal(str(o["total_amount"])) for o in revenue.data) if revenue.data else 0

        # Get pending orders
        pending = db.table("orders").select("id", count="exact").eq("status", "pending").execute()

        # Get pending reviews
        pending_reviews = db.table("reviews").select("id", count="exact").eq("status", "pending").execute()

        return APIResponse(
            success=True,
            data={
                "total_products": products.count or 0,
                "total_orders": orders.count or 0,
                "total_customers": users.count or 0,
                "total_revenue": float(total_revenue),
                "pending_orders": pending.count or 0,
                "pending_reviews": pending_reviews.count or 0,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard stats.",
        )


# ===========================================
# PRODUCTS MANAGEMENT
# ===========================================

@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def admin_list_products(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    """
    List all products (including drafts).
    """
    try:
        db = get_supabase_admin()

        query = db.table("products").select("*", count="exact")

        if status:
            query = query.eq("status", status)

        if search:
            query = query.ilike("name", f"%{search}%")

        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        products = [ProductResponse(**p) for p in result.data]

        return PaginatedResponse(
            data=products,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch products.",
        )


@router.post("/products", response_model=APIResponse[ProductResponse])
async def admin_create_product(product_data: ProductCreate, admin: CurrentAdmin):
    """
    Create a new product.
    """
    try:
        db = get_supabase_admin()

        # Generate slug if not provided
        slug = product_data.slug or product_data.name.lower().replace(" ", "-")

        result = db.table("products").insert({
            **product_data.model_dump(exclude={"variants"}),
            "slug": slug,
        }).execute()

        # Create variants if provided
        if product_data.variants:
            for variant in product_data.variants:
                db.table("product_variants").insert({
                    "product_id": result.data[0]["id"],
                    **variant.model_dump(exclude={"id"}),
                }).execute()

        return APIResponse(
            success=True,
            message="Product created successfully.",
            data=ProductResponse(**result.data[0]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}",
        )


@router.patch("/products/{product_id}", response_model=APIResponse[ProductResponse])
async def admin_update_product(
    product_id: str,
    product_data: ProductUpdate,
    admin: CurrentAdmin,
):
    """
    Update a product.
    """
    try:
        db = get_supabase_admin()

        update_data = product_data.model_dump(exclude_none=True, exclude={"variants"})

        if not update_data and not product_data.variants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update.",
            )

        if update_data:
            result = db.table("products").update(update_data).eq("id", product_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found.",
                )

        # Fetch updated product
        product = db.table("products").select("*").eq("id", product_id).single().execute()

        return APIResponse(
            success=True,
            message="Product updated successfully.",
            data=ProductResponse(**product.data),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product.",
        )


@router.delete("/products/{product_id}", response_model=APIResponse)
async def admin_delete_product(product_id: str, admin: CurrentAdmin):
    """
    Delete a product (archives it).
    """
    try:
        db = get_supabase_admin()

        # Soft delete - archive
        db.table("products").update({"status": "archived"}).eq("id", product_id).execute()

        return APIResponse(success=True, message="Product archived.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product.",
        )


# ===========================================
# CATEGORIES MANAGEMENT
# ===========================================

@router.post("/categories", response_model=APIResponse[CategoryResponse])
async def admin_create_category(category_data: CategoryCreate, admin: CurrentAdmin):
    """
    Create a new category.
    """
    try:
        db = get_supabase_admin()

        slug = category_data.slug or category_data.name.lower().replace(" ", "-")

        result = db.table("categories").insert({
            **category_data.model_dump(),
            "slug": slug,
        }).execute()

        return APIResponse(
            success=True,
            message="Category created.",
            data=CategoryResponse(**result.data[0]),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category.",
        )


@router.patch("/categories/{category_id}", response_model=APIResponse[CategoryResponse])
async def admin_update_category(
    category_id: str,
    category_data: CategoryUpdate,
    admin: CurrentAdmin,
):
    """
    Update a category.
    """
    try:
        db = get_supabase_admin()

        update_data = category_data.model_dump(exclude_none=True)

        result = db.table("categories").update(update_data).eq("id", category_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        return APIResponse(
            success=True,
            message="Category updated.",
            data=CategoryResponse(**result.data[0]),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category.",
        )


# ===========================================
# ORDERS MANAGEMENT
# ===========================================

@router.get("/orders", response_model=PaginatedResponse[OrderResponse])
async def admin_list_orders(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
):
    """
    List all orders.
    """
    try:
        db = get_supabase_admin()

        query = db.table("orders").select("*, order_items(*)", count="exact")

        if status:
            query = query.eq("status", status)

        if payment_status:
            query = query.eq("payment_status", payment_status)

        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        orders = [OrderResponse(**o) for o in result.data]

        return PaginatedResponse(
            data=orders,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders.",
        )


@router.patch("/orders/{order_id}", response_model=APIResponse[OrderResponse])
async def admin_update_order(
    order_id: str,
    order_data: OrderUpdate,
    admin: CurrentAdmin,
):
    """
    Update order status.
    """
    try:
        db = get_supabase_admin()

        update_data = order_data.model_dump(exclude_none=True)

        # Add timestamps based on status
        if order_data.status == "shipped":
            from datetime import datetime
            update_data["shipped_at"] = datetime.utcnow().isoformat()
        elif order_data.status == "delivered":
            from datetime import datetime
            update_data["delivered_at"] = datetime.utcnow().isoformat()

        result = db.table("orders").update(update_data).eq("id", order_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        # Fetch complete order
        order = db.table("orders").select("*, order_items(*)").eq("id", order_id).single().execute()

        return APIResponse(
            success=True,
            message="Order updated.",
            data=OrderResponse(**order.data),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order.",
        )


# ===========================================
# REVIEWS MODERATION
# ===========================================

@router.get("/reviews/pending", response_model=PaginatedResponse[ReviewResponse])
async def admin_pending_reviews(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    List pending reviews for moderation.
    """
    try:
        db = get_supabase_admin()

        query = db.table("reviews").select(
            "*, profiles(full_name, avatar_url)", count="exact"
        ).eq("status", "pending").order("created_at", desc=True)

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


@router.patch("/reviews/{review_id}", response_model=APIResponse)
async def admin_moderate_review(
    review_id: str,
    moderation: ReviewModerate,
    admin: CurrentAdmin,
):
    """
    Approve or reject a review.
    """
    try:
        db = get_supabase_admin()

        update_data = {
            "status": moderation.status,
            "moderation_note": moderation.moderation_note,
        }

        result = db.table("reviews").update(update_data).eq("id", review_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found.",
            )

        return APIResponse(
            success=True,
            message=f"Review {moderation.status}.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate review.",
        )


# ===========================================
# USERS MANAGEMENT
# ===========================================

@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def admin_list_users(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    """
    List all users.
    """
    try:
        db = get_supabase_admin()

        query = db.table("profiles").select("*", count="exact")

        if role:
            query = query.eq("role", role)

        if search:
            query = query.or_(f"email.ilike.%{search}%,full_name.ilike.%{search}%")

        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        users = [UserResponse(**u) for u in result.data]

        return PaginatedResponse(
            data=users,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users.",
        )


@router.get("/users/{user_id}", response_model=APIResponse)
async def admin_get_user_details(user_id: str, admin: CurrentAdmin):
    """
    Get detailed information about a specific user.
    Includes profile, statistics, and recent activity.
    """
    try:
        db = get_supabase_admin()

        # Get user profile
        user = db.table("profiles").select("*").eq("id", user_id).single().execute()

        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        # Get user statistics
        orders = db.table("orders").select("id, total_amount, status, created_at").eq("user_id", user_id).execute()

        total_orders = len(orders.data) if orders.data else 0
        total_spent = sum(float(o.get("total_amount", 0)) for o in orders.data) if orders.data else 0

        # Get addresses count
        addresses = db.table("addresses").select("id", count="exact").eq("user_id", user_id).execute()

        # Get reviews count
        reviews = db.table("reviews").select("id", count="exact").eq("user_id", user_id).execute()

        # Get wishlist count
        wishlist = db.table("wishlist_items").select("id", count="exact").eq("user_id", user_id).execute()

        return APIResponse(
            success=True,
            data={
                **user.data,
                "statistics": {
                    "total_orders": total_orders,
                    "total_spent": total_spent,
                    "addresses_count": addresses.count or 0,
                    "reviews_count": reviews.count or 0,
                    "wishlist_count": wishlist.count or 0,
                },
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user details.",
        )


@router.get("/users/{user_id}/orders", response_model=PaginatedResponse[OrderResponse])
async def admin_get_user_orders(
    user_id: str,
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    Get all orders for a specific user.
    """
    try:
        db = get_supabase_admin()

        query = db.table("orders").select("*, order_items(*)", count="exact").eq("user_id", user_id)
        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        orders = [OrderResponse(**o) for o in result.data] if result.data else []

        return PaginatedResponse(
            data=orders,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user orders.",
        )


@router.get("/users/{user_id}/addresses", response_model=APIResponse)
async def admin_get_user_addresses(user_id: str, admin: CurrentAdmin):
    """
    Get all addresses for a specific user.
    """
    try:
        db = get_supabase_admin()

        result = db.table("addresses").select("*").eq("user_id", user_id).execute()

        return APIResponse(
            success=True,
            data=result.data or [],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user addresses.",
        )


@router.get("/users/{user_id}/reviews", response_model=APIResponse)
async def admin_get_user_reviews(user_id: str, admin: CurrentAdmin):
    """
    Get all reviews written by a specific user.
    """
    try:
        db = get_supabase_admin()

        result = db.table("reviews").select("*, products(name, slug)").eq("user_id", user_id).order("created_at", desc=True).execute()

        return APIResponse(
            success=True,
            data=result.data or [],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user reviews.",
        )


@router.patch("/users/{user_id}/status", response_model=APIResponse)
async def admin_toggle_user_status(
    user_id: str,
    admin: CurrentAdmin,
    is_active: bool = Query(...),
):
    """
    Enable or disable a user account.
    """
    try:
        db = get_supabase_admin()

        result = db.table("profiles").update({"is_active": is_active}).eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        status_text = "enabled" if is_active else "disabled"
        return APIResponse(success=True, message=f"User account {status_text}.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status.",
        )


@router.patch("/users/{user_id}/role", response_model=APIResponse)
async def admin_update_user_role(
    user_id: str,
    admin: CurrentAdmin,
    role: str = Query(..., pattern="^(customer|admin)$"),
):
    """
    Update user role.
    """
    try:
        db = get_supabase_admin()

        result = db.table("profiles").update({"role": role}).eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return APIResponse(success=True, message=f"User role updated to {role}.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role.",
        )


# ===========================================
# ORDER MANAGEMENT (ADMIN)
# ===========================================

@router.get("/orders/cancellations", response_model=PaginatedResponse)
async def admin_get_cancellations(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    Get all cancelled orders with reasons.
    """
    try:
        db = get_supabase_admin()

        query = db.table("orders").select(
            "*, profiles(full_name, email)",
            count="exact"
        ).eq("status", "cancelled").order("cancelled_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        return PaginatedResponse(
            data=result.data or [],
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cancellations.",
        )


@router.get("/orders/returns", response_model=PaginatedResponse)
async def admin_get_returns(
    admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
):
    """
    Get all return requests.
    """
    try:
        db = get_supabase_admin()

        query = db.table("orders").select(
            "*, profiles(full_name, email)",
            count="exact"
        ).eq("status", "returned").order("updated_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        return PaginatedResponse(
            data=result.data or [],
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch return requests.",
        )


@router.post("/orders/{order_id}/approve-return", response_model=APIResponse)
async def admin_approve_return(
    order_id: str,
    admin: CurrentAdmin,
):
    """
    Approve return request and initiate refund.
    """
    try:
        db = get_supabase_admin()

        # Get order
        order_result = db.table("orders").select("status, payment_status, total_amount").eq(
            "id", order_id
        ).single().execute()

        if not order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        if order_result.data["status"] != "returned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in returned status.",
            )

        # Update to refunded status
        db.table("orders").update({
            "status": "refunded",
            "payment_status": "refunded",
        }).eq("id", order_id).execute()

        return APIResponse(
            success=True,
            message="Return approved. Refund will be processed within 3-5 business days.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve return.",
        )


@router.post("/orders/{order_id}/reject-return", response_model=APIResponse)
async def admin_reject_return(
    order_id: str,
    admin: CurrentAdmin,
    reason: str = Query(..., min_length=10),
):
    """
    Reject return request.
    """
    try:
        db = get_supabase_admin()

        # Get order
        order_result = db.table("orders").select("status").eq("id", order_id).single().execute()

        if not order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        if order_result.data["status"] != "returned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not in returned status.",
            )

        # Revert to delivered
        db.table("orders").update({
            "status": "delivered",
            "admin_notes": f"Return rejected: {reason}",
        }).eq("id", order_id).execute()

        return APIResponse(
            success=True,
            message="Return request rejected.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject return.",
        )


@router.patch("/orders/{order_id}/tracking", response_model=APIResponse)
async def admin_update_tracking(
    order_id: str,
    admin: CurrentAdmin,
    tracking_number: str = Query(...),
    tracking_url: Optional[str] = None,
):
    """
    Update order tracking information.
    """
    try:
        db = get_supabase_admin()

        update_data = {
            "tracking_number": tracking_number,
            "status": "shipped",
        }

        if tracking_url:
            update_data["tracking_url"] = tracking_url

        # Add shipped_at timestamp if not set
        from datetime import datetime
        order = db.table("orders").select("shipped_at").eq("id", order_id).single().execute()
        if order.data and not order.data.get("shipped_at"):
            update_data["shipped_at"] = datetime.now().isoformat()

        result = db.table("orders").update(update_data).eq("id", order_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        return APIResponse(
            success=True,
            message="Tracking information updated.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tracking.",
        )


@router.patch("/orders/{order_id}/mark-delivered", response_model=APIResponse)
async def admin_mark_delivered(
    order_id: str,
    admin: CurrentAdmin,
):
    """
    Mark order as delivered.
    """
    try:
        db = get_supabase_admin()

        from datetime import datetime
        result = db.table("orders").update({
            "status": "delivered",
            "delivered_at": datetime.now().isoformat(),
        }).eq("id", order_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        return APIResponse(
            success=True,
            message="Order marked as delivered.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark as delivered.",
        )


@router.get("/orders/statistics", response_model=APIResponse)
async def admin_get_order_statistics(admin: CurrentAdmin):
    """
    Get order statistics for admin dashboard.
    """
    try:
        db = get_supabase_admin()

        # Get order counts by status
        orders = db.table("orders").select("status, total_amount, payment_status").execute()

        stats = {
            "total_orders": len(orders.data) if orders.data else 0,
            "pending": 0,
            "confirmed": 0,
            "shipped": 0,
            "delivered": 0,
            "cancelled": 0,
            "returned": 0,
            "total_revenue": 0,
            "pending_refunds": 0,
        }

        if orders.data:
            for order in orders.data:
                status = order["status"]
                if status in stats:
                    stats[status] += 1

                if order["payment_status"] == "paid":
                    stats["total_revenue"] += float(order["total_amount"])

                if order["status"] == "returned":
                    stats["pending_refunds"] += float(order["total_amount"])

        return APIResponse(success=True, data=stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order statistics.",
        )
