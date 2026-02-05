"""
Payment Endpoints
Razorpay payment integration
"""

import razorpay
import hmac
import hashlib
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Annotated

from app.core.config import settings
from app.core.supabase import supabase
from app.middleware.auth import get_current_user
from app.schemas.payment import (
    CreatePaymentOrderRequest,
    CreatePaymentOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
    PaymentWebhookData,
    PaymentStatus
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
)

# Type alias for current user
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.post("/create-order", response_model=CreatePaymentOrderResponse)
async def create_payment_order(
    request: CreatePaymentOrderRequest,
    current_user: CurrentUser
):
    """
    Create Razorpay order for payment

    Steps:
    1. Verify order exists and belongs to user
    2. Create Razorpay order
    3. Update order with Razorpay order ID
    4. Return order details for frontend
    """
    try:
        # Get order from database
        order_result = supabase.table("orders").select("*").eq(
            "id", request.order_id
        ).eq("user_id", current_user["id"]).execute()

        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_result.data[0]

        # Check if order is already paid
        if order.get("payment_status") == "paid":
            raise HTTPException(status_code=400, detail="Order already paid")

        # Calculate amount in paise (Razorpay uses smallest currency unit)
        amount_in_paise = int(float(order["total_amount"]) * 100)

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order['id']}",
            "notes": {
                "order_id": order["id"],
                "user_id": current_user["id"],
                "user_email": current_user.get("email", "")
            }
        })

        # Update order with Razorpay order ID
        supabase.table("orders").update({
            "razorpay_order_id": razorpay_order["id"],
            "payment_method": "razorpay"
        }).eq("id", request.order_id).execute()

        return CreatePaymentOrderResponse(
            success=True,
            razorpay_order_id=razorpay_order["id"],
            amount=amount_in_paise,
            currency="INR",
            key_id=settings.razorpay_key_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/verify", response_model=VerifyPaymentResponse)
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: CurrentUser
):
    """
    Verify Razorpay payment signature

    Steps:
    1. Verify signature using Razorpay SDK
    2. Update order payment status
    3. Return verification result
    """
    try:
        # Verify signature
        params_dict = {
            "razorpay_order_id": request.razorpay_order_id,
            "razorpay_payment_id": request.razorpay_payment_id,
            "razorpay_signature": request.razorpay_signature
        }

        # Razorpay signature verification
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            payment_verified = True
        except razorpay.errors.SignatureVerificationError:
            payment_verified = False

        if payment_verified:
            # Update order status
            supabase.table("orders").update({
                "payment_status": "paid",
                "razorpay_payment_id": request.razorpay_payment_id,
                "status": "confirmed",
                "paid_at": "now()"
            }).eq("id", request.order_id).eq("user_id", current_user["id"]).execute()

            return VerifyPaymentResponse(
                success=True,
                message="Payment verified successfully",
                payment_verified=True,
                order_id=request.order_id,
                payment_id=request.razorpay_payment_id
            )
        else:
            # Mark payment as failed
            supabase.table("orders").update({
                "payment_status": "failed"
            }).eq("id", request.order_id).execute()

            return VerifyPaymentResponse(
                success=False,
                message="Payment verification failed",
                payment_verified=False,
                order_id=request.order_id
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Payment verification error: {str(e)}"
        )


@router.post("/webhook")
async def payment_webhook(
    webhook_data: PaymentWebhookData,
    x_razorpay_signature: str = Header(None)
):
    """
    Handle Razorpay webhooks

    Events:
    - payment.captured: Payment successful
    - payment.failed: Payment failed
    - order.paid: Order paid
    """
    try:
        # Verify webhook signature
        if settings.razorpay_webhook_secret:
            body = webhook_data.model_dump_json()
            expected_signature = hmac.new(
                settings.razorpay_webhook_secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()

            if x_razorpay_signature != expected_signature:
                raise HTTPException(status_code=401, detail="Invalid signature")

        event = webhook_data.event
        payload = webhook_data.payload

        # Handle different events
        if event == "payment.captured":
            # Payment successful
            payment = payload.get("payment", {}).get("entity", {})
            order_id = payment.get("notes", {}).get("order_id")

            if order_id:
                supabase.table("orders").update({
                    "payment_status": "paid",
                    "status": "confirmed",
                    "paid_at": "now()"
                }).eq("id", order_id).execute()

        elif event == "payment.failed":
            # Payment failed
            payment = payload.get("payment", {}).get("entity", {})
            order_id = payment.get("notes", {}).get("order_id")

            if order_id:
                supabase.table("orders").update({
                    "payment_status": "failed"
                }).eq("id", order_id).execute()

        return {"success": True, "message": "Webhook processed"}

    except HTTPException:
        raise
    except Exception as e:
        # Log error but return success to prevent Razorpay retries
        print(f"Webhook error: {str(e)}")
        return {"success": True, "message": "Webhook received"}


@router.get("/status/{order_id}", response_model=PaymentStatus)
async def get_payment_status(
    order_id: str,
    current_user: CurrentUser
):
    """Get payment status for an order"""
    try:
        order_result = supabase.table("orders").select(
            "id, payment_status, razorpay_payment_id, razorpay_order_id, total_amount, paid_at"
        ).eq("id", order_id).eq("user_id", current_user["id"]).execute()

        if not order_result.data:
            raise HTTPException(status_code=404, detail="Order not found")

        order = order_result.data[0]

        return PaymentStatus(
            success=True,
            order_id=order["id"],
            payment_status=order.get("payment_status", "pending"),
            razorpay_payment_id=order.get("razorpay_payment_id"),
            razorpay_order_id=order.get("razorpay_order_id"),
            amount=int(float(order["total_amount"]) * 100) if order.get("total_amount") else None,
            currency="INR",
            paid_at=order.get("paid_at")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get payment status: {str(e)}"
        )
