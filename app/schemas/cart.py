"""
Shopping cart schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    """Base cart item schema."""

    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0, le=100)


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart."""

    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item."""

    quantity: int = Field(..., gt=0, le=100)


class CartItem(BaseModel):
    """Cart item with product details."""

    id: str
    product_id: str
    product_name: str
    product_slug: str
    product_image: Optional[str] = None
    variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    sale_price: Optional[Decimal] = None
    total_price: Decimal
    stock_quantity: int
    is_available: bool = True
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartSummary(BaseModel):
    """Cart totals summary."""

    subtotal: Decimal
    discount: Decimal = Decimal("0")
    shipping: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    total: Decimal


class Cart(BaseModel):
    """Complete cart with items and summary."""

    items: List[CartItem] = Field(default_factory=list)
    item_count: int = 0
    summary: CartSummary

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    """Cart API response."""

    success: bool = True
    cart: Cart
    message: Optional[str] = None


class ApplyCouponRequest(BaseModel):
    """Request to apply a coupon."""

    coupon_code: str = Field(..., min_length=1, max_length=50)


class CouponResponse(BaseModel):
    """Coupon validation response."""

    valid: bool
    code: str
    discount_type: str = ""  # "percentage" or "fixed"
    discount_value: Decimal = Decimal("0")
    message: str = ""
