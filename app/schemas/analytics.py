from typing import Any

from pydantic import BaseModel


class DashboardAnalyticsResponse(BaseModel):
    total_products: int
    total_warehouses: int
    inventory_value: float
    low_stock_items: int
    out_of_stock_items: int
    purchase_orders_this_month: int
    inventory_turnover: float
    average_supplier_performance: float
    average_warehouse_utilization: float
    most_moved_products: list[Any]


class InventoryAnalyticsResponse(BaseModel):
    total_inventory_records: int
    total_available_quantity: float
    total_reserved_quantity: float
    total_damaged_quantity: float
    inventory_value: float
    low_stock_items: int
    out_of_stock_items: int
    most_moved_products: list[Any]


class SupplierAnalyticsResponse(BaseModel):
    suppliers: list[Any]


class WarehouseAnalyticsResponse(BaseModel):
    warehouses: list[Any]