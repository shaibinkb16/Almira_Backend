"""
Authentication endpoints.
Handles user registration, login, and token management.
Uses Supabase Auth for actual authentication.
"""

from fastapi import APIRouter, HTTPException, status

from app.core.supabase import get_supabase_client
from app.schemas.user import (
    UserCreate,
    LoginRequest,
    LoginResponse,
    UserResponse,
    PasswordResetRequest,
    TokenRefreshRequest,
)
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserResponse])
async def register(user_data: UserCreate):
    """
    Register a new user account.

    - Creates user in Supabase Auth
    - Profile is automatically created via database trigger
    - Sends email verification
    """
    try:
        client = get_supabase_client()

        # Register with Supabase Auth
        result = client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "phone": user_data.phone,
                }
            }
        })

        if result.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Please try again.",
            )

        return APIResponse(
            success=True,
            message="Registration successful. Please check your email to verify your account.",
            data=UserResponse(
                id=result.user.id,
                email=result.user.email,
                full_name=user_data.full_name,
            ),
        )

    except Exception as e:
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login with email and password.

    Returns access and refresh tokens.
    """
    try:
        client = get_supabase_client()

        result = client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })

        if result.user is None or result.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        # Get user profile
        profile = client.table("profiles").select("*").eq("id", result.user.id).single().execute()

        return LoginResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            expires_in=result.session.expires_in or 3600,
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                full_name=profile.data.get("full_name") if profile.data else None,
                avatar_url=profile.data.get("avatar_url") if profile.data else None,
                phone=profile.data.get("phone") if profile.data else None,
                role=profile.data.get("role", "customer") if profile.data else "customer",
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        client = get_supabase_client()

        result = client.auth.refresh_session(request.refresh_token)

        if result.user is None or result.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        # Get user profile
        profile = client.table("profiles").select("*").eq("id", result.user.id).single().execute()

        return LoginResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            expires_in=result.session.expires_in or 3600,
            user=UserResponse(
                id=result.user.id,
                email=result.user.email,
                full_name=profile.data.get("full_name") if profile.data else None,
                avatar_url=profile.data.get("avatar_url") if profile.data else None,
                phone=profile.data.get("phone") if profile.data else None,
                role=profile.data.get("role", "customer") if profile.data else "customer",
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token.",
        )


@router.post("/logout")
async def logout():
    """
    Logout current user.

    Note: This is mainly for server-side cleanup.
    Client should also clear stored tokens.
    """
    return APIResponse(
        success=True,
        message="Logged out successfully.",
    )


@router.post("/password/reset")
async def request_password_reset(request: PasswordResetRequest):
    """
    Request password reset email.
    """
    try:
        client = get_supabase_client()

        client.auth.reset_password_email(request.email)

        # Always return success to prevent email enumeration
        return APIResponse(
            success=True,
            message="If an account exists with this email, you will receive a password reset link.",
        )

    except Exception:
        # Still return success to prevent enumeration
        return APIResponse(
            success=True,
            message="If an account exists with this email, you will receive a password reset link.",
        )


@router.post("/password/verify")
async def verify_email():
    """
    Verify email address.

    This is typically handled by Supabase's email verification flow.
    This endpoint exists for custom verification if needed.
    """
    return APIResponse(
        success=True,
        message="Email verification is handled via the link sent to your email.",
    )
