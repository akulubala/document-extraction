from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Product(BaseModel):
    product_sku: str = Field(
        description="The sku of the product. Extract as a digit stripping SKU prefix.",
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
            raise ValueError("Name must not be empty")
        return v