"""
Payment Schemas
Razorpay payment integration schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreatePaymentOrderRequest(BaseModel):
    """Request to create Razorpay order"""
    order_id: str = Field(..., description="Internal order ID")


class CreatePaymentOrderResponse(BaseModel):
    """Razorpay order creation response"""
    success: bool
    razorpay_order_id: str
    amount: int  # Amount in paise (INR)
    currency: str = "INR"
    key_id: str  # Razorpay Key ID for frontend


class VerifyPaymentRequest(BaseModel):
    """Request to verify Razorpay payment"""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    order_id: str  # Internal order ID


class VerifyPaymentResponse(BaseModel):
    """Payment verification response"""
    success: bool
    message: str
    payment_verified: bool
    order_id: str
    payment_id: Optional[str] = None


class PaymentWebhookData(BaseModel):
    """Razorpay webhook payload"""
    event: str
    payload: dict


class PaymentStatus(BaseModel):
    """Payment status response"""
    success: bool
    order_id: str
    payment_status: str  # pending, paid, failed
    razorpay_payment_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    paid_at: Optional[str] = None
