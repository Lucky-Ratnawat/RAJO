from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    category_id: int
    name: str
    slug: str
    description: str | None = None
    sku: str
    base_price: Decimal
    moq: int
    material: str | None = None
    plating: str | None = None
    weight_grams: Decimal | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    sku: str | None = None
    base_price: Decimal | None = None
    moq: int | None = None
    material: str | None = None
    plating: str | None = None
    weight_grams: Decimal | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
