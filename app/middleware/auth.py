"""
Authentication middleware and dependencies.
Handles JWT token validation and user extraction.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.supabase import get_supabase_admin
from app.schemas.user import UserInDB

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """
    Authentication middleware for validating Supabase JWT tokens.
    """

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate a Supabase JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            # Supabase tokens are signed with the JWT secret
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},  # Supabase doesn't always set audience
            )
            return payload
        except JWTError as e:
            return None

    @staticmethod
    async def get_user_from_token(token: str) -> Optional[UserInDB]:
        """
        Get user data from a valid token.

        Args:
            token: Valid JWT token

        Returns:
            UserInDB object or None
        """
        payload = AuthMiddleware.decode_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Fetch user profile from Supabase
        try:
            admin = get_supabase_admin()
            result = admin.table("profiles").select("*").eq("id", user_id).single().execute()

            if result.data:
                return UserInDB(
                    id=result.data["id"],
                    email=payload.get("email", ""),
                    full_name=result.data.get("full_name"),
                    avatar_url=result.data.get("avatar_url"),
                    phone=result.data.get("phone"),
                    role=result.data.get("role", "customer"),
                    is_active=result.data.get("is_active", True),
                    created_at=result.data.get("created_at"),
                    updated_at=result.data.get("updated_at"),
                )
        except Exception as e:
            return None

        return None


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> UserInDB:
    """
    Dependency to get the current authenticated user.
    Raises 401 if not authenticated.

    Args:
        credentials: Bearer token credentials

    Returns:
        Current user object

    Raises:
        HTTPException: If not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthMiddleware.get_user_from_token(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> Optional[UserInDB]:
    """
    Dependency to optionally get the current user.
    Returns None if not authenticated (doesn't raise error).

    Args:
        credentials: Bearer token credentials

    Returns:
        Current user object or None
    """
    if not credentials:
        return None

    return await AuthMiddleware.get_user_from_token(credentials.credentials)


async def get_current_admin(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserInDB:
    """
    Dependency to verify the current user is an admin.

    Args:
        current_user: Current authenticated user

    Returns:
        Admin user object

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[UserInDB, Depends(get_current_user)]
CurrentUserOptional = Annotated[Optional[UserInDB], Depends(get_current_user_optional)]
CurrentAdmin = Annotated[UserInDB, Depends(get_current_admin)]
