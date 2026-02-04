"""
Address schemas for shipping and billing.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


AddressType = Literal["shipping", "billing", "both"]


class AddressBase(BaseModel):
    """Base address schema."""

    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{9,14}$")
    address_line1: str = Field(..., min_length=5, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r"^\d{6}$")  # Indian PIN code
    country: str = Field(default="India", max_length=100)
    address_type: AddressType = "shipping"
    is_default: bool = False
    label: Optional[str] = Field(None, max_length=50)  # "Home", "Office", etc.

    model_config = ConfigDict(str_strip_whitespace=True)


class AddressCreate(AddressBase):
    """Schema for creating an address."""

    pass


class AddressUpdate(BaseModel):
    """Schema for updating an address."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{9,14}$")
    address_line1: Optional[str] = Field(None, min_length=5, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, pattern=r"^\d{6}$")
    country: Optional[str] = Field(None, max_length=100)
    address_type: Optional[AddressType] = None
    is_default: Optional[bool] = None
    label: Optional[str] = Field(None, max_length=50)


class AddressResponse(BaseModel):
    """Address response."""

    id: str
    user_id: str
    full_name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    address_type: AddressType
    is_default: bool
    label: Optional[str] = None
    formatted_address: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **data):
        super().__init__(**data)
        # Generate formatted address
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.city, self.state, self.postal_code, self.country])
        self.formatted_address = ", ".join(parts)


# Indian states for validation
INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    # Union Territories
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]
