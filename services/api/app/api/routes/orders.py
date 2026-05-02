from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_user_db
from app.db.session import get_db
from app.models.catalog import Product, ProductVariant
from app.models.inventory import Inventory
from app.models.ordering import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter()


def _build_order_number() -> str:
    return f"RAJO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


@router.get("", response_model=list[OrderRead])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_user_db),
) -> list[Order]:
    statement = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(selectinload(Order.items))
        .order_by(Order.id.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_user_db),
) -> Order:
    statement = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    order = db.scalar(statement)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return order


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_user_db),
) -> Order:
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order requires items.")

    subtotal = Decimal("0.00")
    order_items: list[OrderItem] = []
    inventory_updates: list[tuple[Inventory, int]] = []

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if product is None or not product.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        variant = None
        if item.variant_id is not None:
            variant = db.get(ProductVariant, item.variant_id)
            if variant is None or variant.product_id != product.id or not variant.is_active:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found.")

        effective_moq = variant.moq_override if variant and variant.moq_override else product.moq
        if item.quantity < effective_moq:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MOQ for {product.name} is {effective_moq}.",
            )

        inventory_statement = select(Inventory).where(
            Inventory.product_id == product.id,
            Inventory.variant_id == item.variant_id,
        )
        inventory = db.scalar(inventory_statement)
        if inventory is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No inventory found for {product.name}.",
            )

        available_for_sale = inventory.available_qty - inventory.reserved_qty
        if item.quantity > available_for_sale:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {available_for_sale} units available for {product.name}.",
            )

        unit_price = variant.price_override if variant and variant.price_override else product.base_price
        line_total = unit_price * item.quantity
        subtotal += line_total

        order_items.append(
            OrderItem(
                product_id=product.id,
                variant_id=item.variant_id,
                product_name_snapshot=product.name,
                sku_snapshot=variant.sku if variant else product.sku,
                unit_price_snapshot=unit_price,
                quantity=item.quantity,
                line_total=line_total,
            )
        )
        inventory_updates.append((inventory, item.quantity))

    order = Order(
        order_number=_build_order_number(),
        user_id=current_user.id,
        status="pending",
        subtotal=subtotal,
        tax_amount=Decimal("0.00"),
        shipping_amount=Decimal("0.00"),
        total_amount=subtotal,
        payment_status="pending",
        notes=payload.notes,
        shipping_address_snapshot=payload.shipping_address_snapshot,
        items=order_items,
    )
    db.add(order)

    for inventory, quantity in inventory_updates:
        inventory.reserved_qty += quantity
        db.add(inventory)

    db.commit()
    db.refresh(order)
    return db.scalar(select(Order).where(Order.id == order.id).options(selectinload(Order.items)))
