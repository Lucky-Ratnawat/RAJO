from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.catalog import Category, Product
from app.schemas.product import ProductRead

router = APIRouter()


@router.get("", response_model=list[ProductRead])
def list_products(
    category_slug: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Product]:
    statement = select(Product).where(Product.is_active.is_(True)).order_by(Product.id.desc())

    if category_slug:
        statement = statement.join(Category).where(Category.slug == category_slug)

    return list(db.scalars(statement).all())
