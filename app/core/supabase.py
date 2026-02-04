"""
Supabase client configuration and utilities.
Provides both anon (public) and service role (admin) clients.
"""

from functools import lru_cache
from typing import Optional

from supabase import Client, create_client

from .config import settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Get Supabase client with anon key.
    Use this for operations that respect RLS policies.

    Returns:
        Supabase client instance
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )


@lru_cache
def get_supabase_admin() -> Client:
    """
    Get Supabase client with service role key.
    CAUTION: This bypasses RLS - use only for admin operations!

    Returns:
        Supabase admin client instance
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )


def get_user_client(access_token: str) -> Client:
    """
    Get Supabase client authenticated as a specific user.
    Use this for user-specific operations that should respect RLS.

    Args:
        access_token: User's Supabase access token

    Returns:
        Authenticated Supabase client
    """
    client = create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )
    client.auth.set_session(access_token, "")
    return client


class SupabaseService:
    """
    Service class for Supabase operations.
    Provides a clean interface for database operations.
    """

    def __init__(self, use_admin: bool = False):
        """
        Initialize Supabase service.

        Args:
            use_admin: If True, use service role key (bypasses RLS)
        """
        self.client = get_supabase_admin() if use_admin else get_supabase_client()

    def table(self, table_name: str):
        """Get a table reference for queries."""
        return self.client.table(table_name)

    def storage(self, bucket_name: str):
        """Get a storage bucket reference."""
        return self.client.storage.from_(bucket_name)

    def auth(self):
        """Get the auth client."""
        return self.client.auth

    async def execute_rpc(self, function_name: str, params: Optional[dict] = None):
        """
        Execute a Postgres function via RPC.

        Args:
            function_name: Name of the function to call
            params: Optional parameters to pass

        Returns:
            Function result
        """
        return self.client.rpc(function_name, params or {}).execute()


# Convenience instances
supabase = SupabaseService(use_admin=False)
supabase_admin = SupabaseService(use_admin=True)
