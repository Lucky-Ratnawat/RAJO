from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.catalog import Category
from app.schemas.category import CategoryRead

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    statement = select(Category).where(Category.is_active.is_(True)).order_by(
        Category.sort_order.asc(), Category.name.asc()
    )
    return list(db.scalars(statement).all())
