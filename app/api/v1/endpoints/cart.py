"""
Shopping cart endpoints.
"""

from decimal import Decimal
from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser
from app.schemas.cart import CartItemCreate, CartItemUpdate, Cart, CartItem, CartSummary, CartResponse
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=CartResponse)
async def get_cart(current_user: CurrentUser):
    """
    Get current user's cart.
    """
    try:
        admin = get_supabase_admin()

        # Get cart items with product details
        result = admin.table("cart_items").select(
            "*, products(id, name, slug, base_price, sale_price, stock_quantity, images)"
        ).eq("user_id", current_user.id).execute()

        items = []
        subtotal = Decimal("0")

        for item in result.data:
            product = item.get("products", {})
            if not product:
                continue

            unit_price = Decimal(str(product.get("sale_price") or product.get("base_price", 0)))
            total = unit_price * item["quantity"]
            subtotal += total

            items.append(CartItem(
                id=item["id"],
                product_id=product["id"],
                product_name=product["name"],
                product_slug=product["slug"],
                product_image=product.get("images", [{}])[0].get("url") if product.get("images") else None,
                variant_id=item.get("variant_id"),
                quantity=item["quantity"],
                unit_price=unit_price,
                sale_price=product.get("sale_price"),
                total_price=total,
                stock_quantity=product.get("stock_quantity", 0),
                is_available=product.get("stock_quantity", 0) >= item["quantity"],
                added_at=item["created_at"],
            ))

        # Calculate totals
        shipping = Decimal("0") if subtotal >= 2999 else Decimal("99")
        tax = (subtotal * Decimal("0.18")).quantize(Decimal("0.01"))  # 18% GST
        total = subtotal + shipping + tax

        return CartResponse(
            cart=Cart(
                items=items,
                item_count=len(items),
                summary=CartSummary(
                    subtotal=subtotal,
                    shipping=shipping,
                    tax=tax,
                    total=total,
                ),
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart.",
        )


@router.post("/items", response_model=APIResponse)
async def add_to_cart(item: CartItemCreate, current_user: CurrentUser):
    """
    Add item to cart.
    """
    try:
        admin = get_supabase_admin()

        # Check if item already in cart
        existing = admin.table("cart_items").select("id, quantity").eq(
            "user_id", current_user.id
        ).eq("product_id", item.product_id).eq(
            "variant_id", item.variant_id
        ).execute()

        if existing.data:
            # Update quantity
            new_qty = existing.data[0]["quantity"] + item.quantity
            admin.table("cart_items").update({"quantity": new_qty}).eq(
                "id", existing.data[0]["id"]
            ).execute()
        else:
            # Insert new item
            admin.table("cart_items").insert({
                "user_id": current_user.id,
                "product_id": item.product_id,
                "variant_id": item.variant_id,
                "quantity": item.quantity,
            }).execute()

        return APIResponse(success=True, message="Item added to cart.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart.",
        )


@router.patch("/items/{item_id}", response_model=APIResponse)
async def update_cart_item(item_id: str, update: CartItemUpdate, current_user: CurrentUser):
    """
    Update cart item quantity.
    """
    try:
        admin = get_supabase_admin()

        result = admin.table("cart_items").update({
            "quantity": update.quantity
        }).eq("id", item_id).eq("user_id", current_user.id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found.",
            )

        return APIResponse(success=True, message="Cart updated.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart.",
        )


@router.delete("/items/{item_id}", response_model=APIResponse)
async def remove_from_cart(item_id: str, current_user: CurrentUser):
    """
    Remove item from cart.
    """
    try:
        admin = get_supabase_admin()

        admin.table("cart_items").delete().eq("id", item_id).eq("user_id", current_user.id).execute()

        return APIResponse(success=True, message="Item removed from cart.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item.",
        )


@router.delete("", response_model=APIResponse)
async def clear_cart(current_user: CurrentUser):
    """
    Clear entire cart.
    """
    try:
        admin = get_supabase_admin()

        admin.table("cart_items").delete().eq("user_id", current_user.id).execute()

        return APIResponse(success=True, message="Cart cleared.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart.",
        )
