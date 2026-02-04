"""
Product schemas for catalog management.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductImage(BaseModel):
    """Product image schema."""

    url: str
    alt: Optional[str] = None
    is_primary: bool = False


class ProductVariant(BaseModel):
    """Product variant (size, color, etc.)."""

    id: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=50)
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    price_adjustment: Decimal = Field(default=Decimal("0"), ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductBase(BaseModel):
    """Base product schema."""

    name: str = Field(..., min_length=2, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)

    # Pricing (in INR)
    base_price: Decimal = Field(..., gt=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    # Inventory
    sku: str = Field(..., min_length=1, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)

    # Categorization
    category_id: Optional[str] = None

    # Status
    status: Literal["draft", "active", "out_of_stock", "archived"] = "draft"

    # SEO
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=300)

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, v, info):
        """Ensure sale price is less than base price."""
        if v is not None and "base_price" in info.data:
            if v >= info.data["base_price"]:
                raise ValueError("Sale price must be less than base price")
        return v


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Jewelry-specific fields
    material: Optional[str] = None  # Gold, Silver, Platinum, etc.
    purity: Optional[str] = None  # 22K, 18K, 925, etc.
    weight: Optional[Decimal] = None  # in grams
    gemstones: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    base_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[str] = None
    status: Optional[Literal["draft", "active", "out_of_stock", "archived"]] = None
    images: Optional[List[ProductImage]] = None
    variants: Optional[List[ProductVariant]] = None
    tags: Optional[List[str]] = None
    material: Optional[str] = None
    purity: Optional[str] = None
    weight: Optional[Decimal] = None
    gemstones: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=100)
    meta_description: Optional[str] = Field(None, max_length=300)


class ProductInDB(ProductBase):
    """Product as stored in database."""

    id: str
    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    material: Optional[str] = None
    purity: Optional[str] = None
    weight: Optional[Decimal] = None
    gemstones: Optional[str] = None
    rating: Decimal = Field(default=Decimal("0"))
    review_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(BaseModel):
    """Product response for API."""

    id: str
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    base_price: Decimal
    sale_price: Optional[Decimal] = None
    sku: str
    stock_quantity: int
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    status: str
    images: List[ProductImage] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    material: Optional[str] = None
    purity: Optional[str] = None
    weight: Optional[Decimal] = None
    gemstones: Optional[str] = None
    rating: Decimal = Field(default=Decimal("0"))
    review_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Product list item (lighter response)."""

    id: str
    name: str
    slug: str
    base_price: Decimal
    sale_price: Optional[Decimal] = None
    status: str
    images: List[ProductImage] = Field(default_factory=list)
    rating: Decimal = Field(default=Decimal("0"))
    review_count: int = Field(default=0)
    is_new: bool = False
    is_featured: bool = False

    model_config = ConfigDict(from_attributes=True)


class ProductFilter(BaseModel):
    """Product filtering parameters."""

    category_id: Optional[str] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = None
    material: Optional[str] = None
    purity: Optional[str] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    in_stock: Optional[bool] = None
