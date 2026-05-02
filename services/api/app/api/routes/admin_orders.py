from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_admin_db
from app.models.inventory import Inventory
from app.models.ordering import Order
from app.schemas.order import OrderRead, OrderStatusUpdate

router = APIRouter()

FINAL_STATUSES = {"delivered", "cancelled"}


@router.get("", response_model=list[OrderRead])
def list_admin_orders(db: Session = Depends(get_admin_db)) -> list[Order]:
    statement = select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())
    return list(db.scalars(statement).all())


@router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_admin_db)
) -> Order:
    statement = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    order = db.scalar(statement)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    new_status = payload.status.lower()
    old_status = order.status.lower()

    if new_status == old_status:
        return order

    if new_status == "cancelled" and old_status != "cancelled":
        for item in order.items:
            inventory = db.scalar(
                select(Inventory).where(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == item.variant_id,
                )
            )
            if inventory is not None:
                inventory.reserved_qty = max(0, inventory.reserved_qty - item.quantity)
                db.add(inventory)

    if new_status == "delivered" and old_status != "delivered":
        for item in order.items:
            inventory = db.scalar(
                select(Inventory).where(
                    Inventory.product_id == item.product_id,
                    Inventory.variant_id == item.variant_id,
                )
            )
            if inventory is not None:
                inventory.reserved_qty = max(0, inventory.reserved_qty - item.quantity)
                inventory.available_qty = max(0, inventory.available_qty - item.quantity)
                db.add(inventory)

    order.status = new_status
    db.add(order)
    db.commit()
    db.refresh(order)
    return db.scalar(select(Order).where(Order.id == order.id).options(selectinload(Order.items)))
