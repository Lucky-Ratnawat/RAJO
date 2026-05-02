from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_db
from app.models.catalog import Product, ProductVariant
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate

router = APIRouter()


@router.get("", response_model=list[InventoryRead])
def list_inventory(db: Session = Depends(get_admin_db)) -> list[Inventory]:
    statement = select(Inventory).order_by(Inventory.id.desc())
    return list(db.scalars(statement).all())


@router.post("", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory(payload: InventoryCreate, db: Session = Depends(get_admin_db)) -> Inventory:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    if payload.variant_id is not None:
        variant = db.get(ProductVariant, payload.variant_id)
        if variant is None or variant.product_id != payload.product_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")

    existing = db.scalar(
        select(Inventory).where(
            Inventory.product_id == payload.product_id,
            Inventory.variant_id == payload.variant_id,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inventory entry already exists for this product/variant.",
        )

    inventory = Inventory(**payload.model_dump())
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


@router.patch("/{inventory_id}", response_model=InventoryRead)
def update_inventory(
    inventory_id: int, payload: InventoryUpdate, db: Session = Depends(get_admin_db)
) -> Inventory:
    inventory = db.get(Inventory, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found.")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(inventory, field, value)

    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory
