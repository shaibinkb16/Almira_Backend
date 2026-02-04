"""
Order endpoints.
"""

from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.schemas.common import APIResponse, PaginatedResponse, create_pagination_meta

router = APIRouter()


@router.get("", response_model=PaginatedResponse[OrderListResponse])
async def list_orders(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
):
    """
    List current user's orders.
    """
    try:
        admin = get_supabase_admin()

        query = admin.table("orders").select("*, order_items(count)", count="exact").eq(
            "user_id", current_user.id
        )

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        orders = [
            OrderListResponse(
                id=o["id"],
                order_number=o["order_number"],
                status=o["status"],
                payment_status=o["payment_status"],
                total_amount=Decimal(str(o["total_amount"])),
                item_count=o.get("order_items", [{}])[0].get("count", 0) if o.get("order_items") else 0,
                created_at=o["created_at"],
            )
            for o in result.data
        ]

        return PaginatedResponse(
            data=orders,
            pagination=create_pagination_meta(page, per_page, result.count or 0),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders.",
        )


@router.get("/{order_id}", response_model=APIResponse[OrderResponse])
async def get_order(order_id: str, current_user: CurrentUser):
    """
    Get order details.
    """
    try:
        admin = get_supabase_admin()

        # Get order
        result = admin.table("orders").select("*, order_items(*)").eq(
            "id", order_id
        ).eq("user_id", current_user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        o = result.data
        return APIResponse(
            success=True,
            data=OrderResponse(**o),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order.",
        )


@router.post("", response_model=APIResponse[OrderResponse])
async def create_order(order_data: OrderCreate, current_user: CurrentUser):
    """
    Create a new order from cart.
    """
    try:
        admin = get_supabase_admin()

        # Get cart items
        cart_result = admin.table("cart_items").select(
            "*, products(id, name, base_price, sale_price, images, stock_quantity)"
        ).eq("user_id", current_user.id).execute()

        if not cart_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty.",
            )

        # Get shipping address
        address_result = admin.table("addresses").select("*").eq(
            "id", order_data.shipping_address_id
        ).eq("user_id", current_user.id).single().execute()

        if not address_result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid shipping address.",
            )

        shipping_address = address_result.data
        billing_address = shipping_address  # Same for now

        # Calculate totals
        subtotal = Decimal("0")
        order_items = []

        for item in cart_result.data:
            product = item["products"]
            price = Decimal(str(product.get("sale_price") or product["base_price"]))
            total = price * item["quantity"]
            subtotal += total

            order_items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "product_image": product.get("images", [{}])[0].get("url") if product.get("images") else None,
                "quantity": item["quantity"],
                "unit_price": float(price),
                "total_price": float(total),
            })

        shipping_amount = Decimal("0") if subtotal >= 2999 else Decimal("99")
        tax_amount = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))
        total_amount = subtotal + shipping_amount + tax_amount

        # Generate order number
        order_number_result = admin.rpc("generate_order_number").execute()
        order_number = order_number_result.data

        # Create order
        order_result = admin.table("orders").insert({
            "order_number": order_number,
            "user_id": current_user.id,
            "status": "pending",
            "payment_status": "pending",
            "payment_method": order_data.payment_method,
            "subtotal": float(subtotal),
            "shipping_amount": float(shipping_amount),
            "tax_amount": float(tax_amount),
            "discount_amount": 0,
            "total_amount": float(total_amount),
            "shipping_address": {
                "full_name": shipping_address["full_name"],
                "phone": shipping_address["phone"],
                "address_line1": shipping_address["address_line1"],
                "address_line2": shipping_address.get("address_line2"),
                "city": shipping_address["city"],
                "state": shipping_address["state"],
                "postal_code": shipping_address["postal_code"],
                "country": shipping_address["country"],
            },
            "billing_address": {
                "full_name": billing_address["full_name"],
                "phone": billing_address["phone"],
                "address_line1": billing_address["address_line1"],
                "address_line2": billing_address.get("address_line2"),
                "city": billing_address["city"],
                "state": billing_address["state"],
                "postal_code": billing_address["postal_code"],
                "country": billing_address["country"],
            },
            "coupon_code": order_data.coupon_code,
            "notes": order_data.notes,
        }).execute()

        order = order_result.data[0]

        # Create order items
        for item in order_items:
            item["order_id"] = order["id"]

        admin.table("order_items").insert(order_items).execute()

        # Clear cart
        admin.table("cart_items").delete().eq("user_id", current_user.id).execute()

        # Fetch complete order
        final_result = admin.table("orders").select("*, order_items(*)").eq(
            "id", order["id"]
        ).single().execute()

        return APIResponse(
            success=True,
            message="Order placed successfully.",
            data=OrderResponse(**final_result.data),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.post("/{order_id}/cancel", response_model=APIResponse)
async def cancel_order(
    order_id: str,
    current_user: CurrentUser,
    reason: Optional[str] = None,
):
    """
    Cancel an order (only if pending or confirmed).
    """
    try:
        admin = get_supabase_admin()

        # Get order
        result = admin.table("orders").select("status, payment_status").eq(
            "id", order_id
        ).eq("user_id", current_user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        if result.data["status"] not in ["pending", "confirmed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled at this stage.",
            )

        # Cancel order
        from datetime import datetime
        admin.table("orders").update({
            "status": "cancelled",
            "cancellation_reason": reason or "Cancelled by customer",
            "cancelled_at": datetime.now().isoformat(),
        }).eq("id", order_id).execute()

        return APIResponse(success=True, message="Order cancelled successfully.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order.",
        )


@router.post("/{order_id}/return", response_model=APIResponse)
async def request_return(
    order_id: str,
    current_user: CurrentUser,
    reason: str = Query(..., min_length=10),
):
    """
    Request a return for delivered order.
    """
    try:
        admin = get_supabase_admin()

        # Get order
        result = admin.table("orders").select("status, payment_status, delivered_at").eq(
            "id", order_id
        ).eq("user_id", current_user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        if result.data["status"] != "delivered":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only delivered orders can be returned.",
            )

        # Check if within return period (7 days)
        from datetime import datetime, timedelta
        delivered_at = datetime.fromisoformat(result.data["delivered_at"])
        if datetime.now() > delivered_at + timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return period has expired (7 days from delivery).",
            )

        # Update order status to returned
        admin.table("orders").update({
            "status": "returned",
            "cancellation_reason": f"Return requested: {reason}",
        }).eq("id", order_id).execute()

        return APIResponse(
            success=True,
            message="Return request submitted. We'll process your refund within 3-5 business days.",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request return.",
        )


@router.get("/{order_id}/track", response_model=APIResponse)
async def track_order(order_id: str, current_user: CurrentUser):
    """
    Get order tracking information.
    """
    try:
        admin = get_supabase_admin()

        # Get order
        result = admin.table("orders").select(
            "order_number, status, tracking_number, tracking_url, created_at, "
            "confirmed_at, shipped_at, delivered_at, cancelled_at"
        ).eq("id", order_id).eq("user_id", current_user.id).single().execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        order = result.data

        # Build tracking timeline
        timeline = []

        if order["created_at"]:
            timeline.append({
                "status": "Order Placed",
                "timestamp": order["created_at"],
                "description": f"Order {order['order_number']} has been placed successfully",
            })

        if order["confirmed_at"]:
            timeline.append({
                "status": "Order Confirmed",
                "timestamp": order["confirmed_at"],
                "description": "Your order has been confirmed and is being prepared",
            })

        if order["shipped_at"]:
            timeline.append({
                "status": "Order Shipped",
                "timestamp": order["shipped_at"],
                "description": "Your order has been shipped",
                "tracking_number": order.get("tracking_number"),
                "tracking_url": order.get("tracking_url"),
            })

        if order["delivered_at"]:
            timeline.append({
                "status": "Order Delivered",
                "timestamp": order["delivered_at"],
                "description": "Your order has been delivered successfully",
            })

        if order["cancelled_at"]:
            timeline.append({
                "status": "Order Cancelled",
                "timestamp": order["cancelled_at"],
                "description": "Your order has been cancelled",
            })

        return APIResponse(
            success=True,
            data={
                "order_number": order["order_number"],
                "current_status": order["status"],
                "tracking_number": order.get("tracking_number"),
                "tracking_url": order.get("tracking_url"),
                "timeline": timeline,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get tracking information.",
        )
