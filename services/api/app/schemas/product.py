from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: str | None
    sku: str
    base_price: Decimal
    moq: int
    material: str | None
    plating: str | None
    weight_grams: Decimal | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
