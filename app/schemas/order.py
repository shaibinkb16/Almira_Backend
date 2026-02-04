"""
Order schemas for e-commerce transactions.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


OrderStatus = Literal[
    "pending",
    "confirmed",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
    "refunded",
]

PaymentStatus = Literal["pending", "paid", "failed", "refunded"]

PaymentMethod = Literal["cod", "card", "upi", "netbanking", "wallet"]


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""

    product_id: str
    variant_id: Optional[str] = None
    quantity: int = Field(..., gt=0, le=100)


class OrderItemResponse(BaseModel):
    """Order item in response."""

    id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderAddress(BaseModel):
    """Shipping/billing address snapshot."""

    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    items: List[OrderItemCreate] = Field(..., min_length=1)
    shipping_address_id: str
    billing_address_id: Optional[str] = None  # Uses shipping if not provided
    payment_method: PaymentMethod
    coupon_code: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class OrderUpdate(BaseModel):
    """Schema for updating an order (admin)."""

    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class OrderInDB(BaseModel):
    """Order as stored in database."""

    id: str
    order_number: str
    user_id: str
    status: OrderStatus
    payment_status: PaymentStatus
    payment_method: PaymentMethod

    # Amounts
    subtotal: Decimal
    shipping_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal

    # Addresses (snapshots)
    shipping_address: OrderAddress
    billing_address: OrderAddress

    # Items
    items: List[OrderItemResponse]

    # Tracking
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None

    # Coupon
    coupon_code: Optional[str] = None

    # Notes
    notes: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(OrderInDB):
    """Order response with user-friendly fields."""

    status_label: str = ""
    payment_status_label: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        status_labels = {
            "pending": "Pending",
            "confirmed": "Confirmed",
            "processing": "Processing",
            "shipped": "Shipped",
            "delivered": "Delivered",
            "cancelled": "Cancelled",
            "refunded": "Refunded",
        }
        payment_labels = {
            "pending": "Payment Pending",
            "paid": "Paid",
            "failed": "Payment Failed",
            "refunded": "Refunded",
        }
        self.status_label = status_labels.get(self.status, self.status)
        self.payment_status_label = payment_labels.get(self.payment_status, self.payment_status)


class OrderListResponse(BaseModel):
    """Order list item (lighter response)."""

    id: str
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: Decimal
    item_count: int
    first_item_image: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderFilter(BaseModel):
    """Order filtering parameters."""

    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
