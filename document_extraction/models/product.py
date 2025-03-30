from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ProductItem(BaseModel):
    """A line item in an invoice."""

    product_sku: str = Field(
        description="The sku of a product",
    )
    product_qty: Optional[int] = Field(
        description="quantity of the product. Extract as a digit",
    )
    product_description: Optional[str] = Field(
        description="description of the product",
    )
    @field_validator("product_sku")
    def product_sku_not_be_empty(cls, v):
        if not v:
            raise ValueError("product sku must not be empty")
        return v

class Product(BaseModel):
    """A representation of information from an invoice."""

    line_items: list[ProductItem] = Field(
        description="A list of all the products in this document"
    )