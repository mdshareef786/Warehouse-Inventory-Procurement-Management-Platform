from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.warehouses import router as warehouse_router
from app.api.suppliers import router as supplier_router
from app.api.categories import router as category_router
from app.api.products import router as product_router
from app.api.inventory import router as inventory_router
from app.api.purchase_orders import router as purchase_order_router
from app.api.alerts import router as alert_router
from app.api.users import router as user_router

from app.api import (
    stock_transfers,
    analytics,
    goods_receipts,
    websocket,
)

from app.background.scheduler import (
    start_background_scheduler,
    stop_background_scheduler,
)

from app.exceptions.custom_exceptions import AppException
from app.exceptions.handlers import (
    app_exception_handler,
    general_exception_handler,
)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # -----------------------------------------------------
    # Startup
    # -----------------------------------------------------

    start_background_scheduler()

    yield

    # -----------------------------------------------------
    # Shutdown
    # -----------------------------------------------------

    await stop_background_scheduler()


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="Warehouse Inventory & Procurement API",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(auth_router)

app.include_router(warehouse_router)

app.include_router(supplier_router)

app.include_router(category_router)

app.include_router(product_router)

app.include_router(inventory_router)

app.include_router(purchase_order_router)

app.include_router(alert_router)

app.include_router(user_router)

app.include_router(
    stock_transfers.router
)

app.include_router(
    analytics.router
)

app.include_router(
    goods_receipts.router
)

app.include_router(
    websocket.router
)


# =========================================================
# EXCEPTION HANDLERS
# =========================================================

app.add_exception_handler(
    AppException,
    app_exception_handler
)

app.add_exception_handler(
    Exception,
    general_exception_handler
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": (
            "Warehouse Inventory & Procurement "
            "API Running Successfully"
        )
    }