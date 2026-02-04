"""
Customer Support & Contact endpoints.
Handles customer inquiries, support tickets, and contact form submissions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, EmailStr

from app.core.supabase import get_supabase_admin
from app.middleware.auth import CurrentUser, CurrentUserOptional
from app.schemas.common import APIResponse, PaginatedResponse, create_pagination_meta

router = APIRouter()


# ===========================================
# SCHEMAS
# ===========================================

class ContactForm(BaseModel):
    """Contact form submission schema"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str
    order_id: Optional[str] = None


class SupportTicket(BaseModel):
    """Support ticket schema"""
    subject: str
    message: str
    category: str  # general, order, product, payment, shipping, return, other
    priority: str = "normal"  # low, normal, high, urgent
    attachments: list[str] = []  # URLs to uploaded images


# ===========================================
# PUBLIC ENDPOINTS
# ===========================================

@router.post("/contact", response_model=APIResponse)
async def submit_contact_form(form_data: ContactForm):
    """
    Submit contact form (public - no auth required).
    Sends email to support team and creates ticket.
    """
    try:
        db = get_supabase_admin()

        # Create contact submission record
        result = db.table("contact_submissions").insert({
            "name": form_data.name,
            "email": form_data.email,
            "phone": form_data.phone,
            "subject": form_data.subject,
            "message": form_data.message,
            "order_id": form_data.order_id,
            "status": "new",
            "source": "website",
        }).execute()

        # TODO: Send email notification to support team
        # send_support_email(form_data)

        return APIResponse(
            success=True,
            message="Thank you for contacting us! We'll get back to you within 24 hours.",
            data={"ticket_id": result.data[0]["id"]},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit contact form. Please try again.",
        )


# ===========================================
# AUTHENTICATED USER ENDPOINTS
# ===========================================

@router.post("/support/ticket", response_model=APIResponse)
async def create_support_ticket(ticket_data: SupportTicket, current_user: CurrentUser):
    """
    Create a support ticket (requires authentication).
    User can track ticket status and get responses.
    """
    try:
        db = get_supabase_admin()

        result = db.table("support_tickets").insert({
            "user_id": current_user.id,
            "subject": ticket_data.subject,
            "message": ticket_data.message,
            "category": ticket_data.category,
            "priority": ticket_data.priority,
            "attachments": ticket_data.attachments,
            "status": "open",
        }).execute()

        # TODO: Send email notification
        # notify_support_team(ticket_data, current_user)

        return APIResponse(
            success=True,
            message="Support ticket created successfully. We'll respond soon!",
            data=result.data[0],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create support ticket.",
        )


@router.get("/support/tickets", response_model=PaginatedResponse)
async def get_my_tickets(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
):
    """
    Get all support tickets created by current user.
    """
    try:
        db = get_supabase_admin()

        query = db.table("support_tickets").select("*", count="exact").eq("user_id", current_user.id)

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)

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
            detail="Failed to fetch support tickets.",
        )


@router.get("/support/tickets/{ticket_id}", response_model=APIResponse)
async def get_ticket_details(ticket_id: str, current_user: CurrentUser):
    """
    Get details of a specific support ticket with all messages.
    """
    try:
        db = get_supabase_admin()

        # Get ticket
        ticket = db.table("support_tickets").select("*").eq("id", ticket_id).eq("user_id", current_user.id).single().execute()

        if not ticket.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found.",
            )

        # Get ticket messages/responses
        messages = db.table("support_messages").select("*").eq("ticket_id", ticket_id).order("created_at").execute()

        return APIResponse(
            success=True,
            data={
                **ticket.data,
                "messages": messages.data or [],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ticket details.",
        )


@router.post("/support/tickets/{ticket_id}/message", response_model=APIResponse)
async def add_ticket_message(
    ticket_id: str,
    message: str,
    current_user: CurrentUser,
    attachments: list[str] = [],
):
    """
    Add a message/reply to an existing support ticket.
    """
    try:
        db = get_supabase_admin()

        # Verify ticket belongs to user
        ticket = db.table("support_tickets").select("id").eq("id", ticket_id).eq("user_id", current_user.id).single().execute()

        if not ticket.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found.",
            )

        # Add message
        result = db.table("support_messages").insert({
            "ticket_id": ticket_id,
            "user_id": current_user.id,
            "message": message,
            "attachments": attachments,
            "is_staff_reply": False,
        }).execute()

        # Update ticket updated_at
        db.table("support_tickets").update({"updated_at": "now()"}).eq("id", ticket_id).execute()

        return APIResponse(
            success=True,
            message="Message added to ticket.",
            data=result.data[0],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add message.",
        )


# ===========================================
# ADMIN ENDPOINTS
# ===========================================

@router.get("/admin/support/tickets", response_model=PaginatedResponse)
async def admin_get_all_tickets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    Admin: Get all support tickets.
    """
    # This would need CurrentAdmin auth
    # For now, placeholder
    pass


@router.post("/admin/support/tickets/{ticket_id}/respond", response_model=APIResponse)
async def admin_respond_to_ticket(ticket_id: str, message: str):
    """
    Admin: Respond to a support ticket.
    """
    # This would need CurrentAdmin auth
    # For now, placeholder
    pass
