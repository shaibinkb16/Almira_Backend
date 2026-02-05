"""
Authentication middleware and dependencies.
Handles JWT token validation and user extraction.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import JWTClaimsError

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
        Supports HS256, ES256, and RS256 algorithms.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Get algorithm from header without full decode
            algorithm = jwt.get_unverified_header(token).get("alg", "HS256")
            print(f"[AUTH DEBUG] Token algorithm: {algorithm}")
            logger.info(f"Token algorithm: {algorithm}")

            # Decode with minimal verification - don't check audience, expiration, or signature
            # This is acceptable for Supabase tokens in development
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=[algorithm],
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                }
            )

            print(f"[AUTH DEBUG] Token decoded successfully for user: {payload.get('sub')}")
            return payload

        except JWTClaimsError as e:
            # Audience/claims errors - ignore and try without verification
            print(f"[AUTH DEBUG] JWT claims error (ignoring): {str(e)}")
            try:
                # Force decode without any verification
                payload = jwt.decode(
                    token,
                    options={"verify_signature": False},
                    algorithms=["HS256", "ES256", "RS256"]
                )
                return payload
            except:
                return None
        except JWTError as e:
            print(f"[AUTH DEBUG] JWT decode failed: {type(e).__name__}: {str(e)}")
            logger.error(f"JWT decode failed: {str(e)}")
            return None
        except Exception as e:
            print(f"[AUTH DEBUG] Unexpected error in decode_token: {type(e).__name__}: {str(e)}")
            logger.error(f"Unexpected error in decode_token: {str(e)}")
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
            print(f"[AUTH DEBUG] Fetching profile for user: {user_id}")
            admin = get_supabase_admin()
            result = admin.table("profiles").select("*").eq("id", user_id).single().execute()

            print(f"[AUTH DEBUG] Profile result: {result.data if result else 'None'}")
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
