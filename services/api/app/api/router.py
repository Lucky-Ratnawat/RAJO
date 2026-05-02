from fastapi import APIRouter

from app.api.routes import (
    admin_categories,
    admin_inventory,
    admin_orders,
    admin_products,
    auth,
    categories,
    health,
    orders,
    products,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(
    admin_categories.router, prefix="/admin/categories", tags=["admin-categories"]
)
api_router.include_router(
    admin_products.router, prefix="/admin/products", tags=["admin-products"]
)
api_router.include_router(
    admin_inventory.router, prefix="/admin/inventory", tags=["admin-inventory"]
)
api_router.include_router(admin_orders.router, prefix="/admin/orders", tags=["admin-orders"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
