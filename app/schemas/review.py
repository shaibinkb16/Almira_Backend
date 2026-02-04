"""
Product review schemas.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


ReviewStatus = Literal["pending", "approved", "rejected"]


class ReviewCreate(BaseModel):
    """Schema for creating a review."""

    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = Field(None, max_length=2000)
    images: List[str] = Field(default_factory=list, max_length=5)


class ReviewUpdate(BaseModel):
    """Schema for updating a review."""

    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = Field(None, max_length=2000)
    images: Optional[List[str]] = Field(None, max_length=5)


class ReviewModerate(BaseModel):
    """Schema for moderating a review (admin)."""

    status: ReviewStatus
    moderation_note: Optional[str] = Field(None, max_length=500)


class ReviewResponse(BaseModel):
    """Review response."""

    id: str
    product_id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    status: ReviewStatus
    is_verified_purchase: bool = False
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewSummary(BaseModel):
    """Product review summary."""

    product_id: str
    average_rating: float
    total_reviews: int
    rating_distribution: dict[int, int] = Field(
        default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    )


class ReviewHelpfulRequest(BaseModel):
    """Mark review as helpful."""

    helpful: bool = True
