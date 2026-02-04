"""Pydantic schemas for API validation."""

from .user import (
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    ProfileUpdate,
)
from .product import (
    ProductCreate,
    ProductUpdate,
    ProductInDB,
    ProductResponse,
    ProductListResponse,
    ProductVariant,
)
from .order import (
    OrderCreate,
    OrderUpdate,
    OrderInDB,
    OrderResponse,
    OrderListResponse,
    OrderItemCreate,
)
from .cart import CartItem, Cart, CartResponse
from .category import CategoryCreate, CategoryUpdate, CategoryResponse
from .review import ReviewCreate, ReviewResponse
from .address import AddressCreate, AddressUpdate, AddressResponse
from .common import (
    APIResponse,
    PaginatedResponse,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "ProfileUpdate",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductInDB",
    "ProductResponse",
    "ProductListResponse",
    "ProductVariant",
    # Order
    "OrderCreate",
    "OrderUpdate",
    "OrderInDB",
    "OrderResponse",
    "OrderListResponse",
    "OrderItemCreate",
    # Cart
    "CartItem",
    "Cart",
    "CartResponse",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    # Review
    "ReviewCreate",
    "ReviewResponse",
    # Address
    "AddressCreate",
    "AddressUpdate",
    "AddressResponse",
    # Common
    "APIResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthResponse",
]
