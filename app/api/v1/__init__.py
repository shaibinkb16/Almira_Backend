"""
API v1 Router - Aggregates all endpoint routers.
"""

from fastapi import APIRouter

from .endpoints import (
    auth,
    users,
    products,
    categories,
    cart,
    orders,
    reviews,
    wishlist,
    addresses,
    admin,
    contact,
    upload,
)

api_router = APIRouter()

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Users
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# Products
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["Products"],
)

# Categories
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
)

# Cart
api_router.include_router(
    cart.router,
    prefix="/cart",
    tags=["Cart"],
)

# Orders
api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"],
)

# Reviews
api_router.include_router(
    reviews.router,
    prefix="/reviews",
    tags=["Reviews"],
)

# Wishlist
api_router.include_router(
    wishlist.router,
    prefix="/wishlist",
    tags=["Wishlist"],
)

# Addresses
api_router.include_router(
    addresses.router,
    prefix="/addresses",
    tags=["Addresses"],
)

# Admin
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)

# Contact & Support
api_router.include_router(
    contact.router,
    prefix="/contact",
    tags=["Contact & Support"],
)

# File Uploads
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["File Uploads"],
)
