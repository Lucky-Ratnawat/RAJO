from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_db
from app.models.catalog import Category, Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductRead])
def list_admin_products(db: Session = Depends(get_admin_db)) -> list[Product]:
    statement = select(Product).order_by(Product.id.desc())
    return list(db.scalars(statement).all())


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_admin_db)) -> Product:
    category = db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    existing_slug = db.scalar(select(Product).where(Product.slug == payload.slug))
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product slug already exists.",
        )

    existing_sku = db.scalar(select(Product).where(Product.sku == payload.sku))
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product SKU already exists.",
        )

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_admin_db)
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "category_id" in updates and db.get(Category, updates["category_id"]) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    if "slug" in updates:
        existing_slug = db.scalar(
            select(Product).where(Product.slug == updates["slug"], Product.id != product_id)
        )
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product slug already exists.",
            )
    if "sku" in updates:
        existing_sku = db.scalar(
            select(Product).where(Product.sku == updates["sku"], Product.id != product_id)
        )
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product SKU already exists.",
            )

    for field, value in updates.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_admin_db)) -> None:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    db.delete(product)
    db.commit()
