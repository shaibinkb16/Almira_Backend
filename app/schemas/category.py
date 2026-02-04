"""
Category schemas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool = True
    display_order: int = Field(default=0, ge=0)


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)


class CategoryResponse(BaseModel):
    """Category response."""

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool
    display_order: int
    product_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryTreeNode(CategoryResponse):
    """Category with nested children for tree structure."""

    children: List["CategoryTreeNode"] = Field(default_factory=list)


# Update forward reference
CategoryTreeNode.model_rebuild()
