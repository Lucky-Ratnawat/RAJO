from pydantic import BaseModel, ConfigDict


class InventoryBase(BaseModel):
    product_id: int
    variant_id: int | None = None
    available_qty: int = 0
    reserved_qty: int = 0
    reorder_level: int = 0


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    available_qty: int | None = None
    reserved_qty: int | None = None
    reorder_level: int | None = None


class InventoryRead(InventoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
