"""
Common schema patterns used across the API.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type for paginated responses
T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    All successful API responses follow this format.
    """

    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response for list endpoints.
    """

    success: bool = True
    data: List[T]
    pagination: "PaginationMeta"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False,
                },
            }
        }
    )


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class ErrorDetail(BaseModel):
    """Error detail object."""

    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """
    Standard error response.
    All API errors follow this format.
    """

    success: bool = False
    error: ErrorDetail

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid input data",
                    "field": "email",
                },
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict[str, str] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


def create_pagination_meta(
    page: int,
    per_page: int,
    total: int,
) -> PaginationMeta:
    """
    Create pagination metadata.

    Args:
        page: Current page number
        per_page: Items per page
        total: Total number of items

    Returns:
        PaginationMeta object
    """
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    return PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
