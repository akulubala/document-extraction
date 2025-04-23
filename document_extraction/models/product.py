from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ProductItem(BaseModel):
    """A line item in an invoice."""

    product_sku: str = Field(
        description="The sku of a product",
    )
    QTE: int = Field(
        description="the quantity of the product.",
    )
    description: Optional[str] = Field(
        description="description of the product",
    )
    @field_validator("product_sku")
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Name must not be empty")
        return v

class Product(BaseModel):
    """A representation of information from an invoice."""

    line_items: list[ProductItem] = Field(
        description="A list of all the products in this document"
    )