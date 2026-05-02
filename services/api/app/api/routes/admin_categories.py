from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_db
from app.models.catalog import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_admin_categories(db: Session = Depends(get_admin_db)) -> list[Category]:
    statement = select(Category).order_by(Category.sort_order.asc(), Category.name.asc())
    return list(db.scalars(statement).all())


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_admin_db)) -> Category:
    existing = db.scalar(select(Category).where(Category.slug == payload.slug))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category slug already exists.",
        )

    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_admin_db)
) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates:
        existing = db.scalar(
            select(Category).where(Category.slug == updates["slug"], Category.id != category_id)
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category slug already exists.",
            )

    for field, value in updates.items():
        setattr(category, field, value)

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_admin_db)) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    db.delete(category)
    db.commit()
