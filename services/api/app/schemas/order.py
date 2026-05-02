from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderCreateItem(BaseModel):
    product_id: int
    variant_id: int | None = None
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderCreateItem]
    notes: str | None = None
    shipping_address_snapshot: dict | None = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    variant_id: int | None
    product_name_snapshot: str
    sku_snapshot: str
    unit_price_snapshot: Decimal
    quantity: int
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    payment_status: str
    notes: str | None
    shipping_address_snapshot: dict | None
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)
