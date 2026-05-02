from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    sort_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
