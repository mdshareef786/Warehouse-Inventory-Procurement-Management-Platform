from app.repositories.analytics_repository import (
    AnalyticsRepository,
)

from app.core.redis import (
    set_cache,
    get_cache,
    delete_cache,
)


class AnalyticsService:

    DASHBOARD_TTL = 300

    DASHBOARD_CACHE_KEY = (
        "analytics:dashboard"
    )

    INVENTORY_CACHE_KEY = (
        "analytics:inventory"
    )

    SUPPLIER_CACHE_KEY = (
        "analytics:suppliers"
    )

    WAREHOUSE_CACHE_KEY = (
        "analytics:warehouses"
    )

    # =========================================================
    # DASHBOARD
    # =========================================================

    @staticmethod
    def get_dashboard(db):

        cached = get_cache(
            AnalyticsService.DASHBOARD_CACHE_KEY
        )

        if cached is not None:
            return cached

        total_products = (
            AnalyticsRepository
            .get_total_products(db)
        )

        total_warehouses = (
            AnalyticsRepository
            .get_total_warehouses(db)
        )

        inventory_value = (
            AnalyticsRepository
            .get_inventory_value(db)
        )

        low_stock_items = (
            AnalyticsRepository
            .get_low_stock_count(db)
        )

        out_of_stock_items = (
            AnalyticsRepository
            .get_out_of_stock_count(db)
        )

        purchase_orders_this_month = (
            AnalyticsRepository
            .get_purchase_orders_this_month(db)
        )

        inventory_turnover = (
            AnalyticsRepository
            .get_inventory_turnover(db)
        )

        suppliers = (
            AnalyticsRepository
            .get_supplier_performance(db)
        )

        warehouses = (
            AnalyticsRepository
            .get_warehouse_analytics(db)
        )

        most_moved_products = (
            AnalyticsRepository
            .get_most_moved_products(db)
        )

        if suppliers:

            average_supplier_performance = round(
                sum(
                    supplier["fulfillment_rate"]
                    for supplier in suppliers
                )
                / len(suppliers),
                2
            )

        else:
            average_supplier_performance = 0

        if warehouses:

            average_warehouse_utilization = round(
                sum(
                    warehouse[
                        "utilization_percentage"
                    ]
                    for warehouse in warehouses
                )
                / len(warehouses),
                2
            )

        else:
            average_warehouse_utilization = 0

        data = {
            "total_products": total_products,
            "total_warehouses": total_warehouses,
            "inventory_value": inventory_value,
            "low_stock_items": low_stock_items,
            "out_of_stock_items": out_of_stock_items,
            "purchase_orders_this_month":
                purchase_orders_this_month,
            "inventory_turnover":
                inventory_turnover,
            "average_supplier_performance":
                average_supplier_performance,
            "average_warehouse_utilization":
                average_warehouse_utilization,
            "most_moved_products":
                most_moved_products,
        }

        set_cache(
            AnalyticsService.DASHBOARD_CACHE_KEY,
            data,
            AnalyticsService.DASHBOARD_TTL,
        )

        return data

    # =========================================================
    # INVENTORY
    # =========================================================

    @staticmethod
    def get_inventory(db):

        cached = get_cache(
            AnalyticsService.INVENTORY_CACHE_KEY
        )

        if cached is not None:
            return cached

        data = (
            AnalyticsRepository
            .get_inventory_analytics(db)
        )

        set_cache(
            AnalyticsService.INVENTORY_CACHE_KEY,
            data,
            AnalyticsService.DASHBOARD_TTL,
        )

        return data

    # =========================================================
    # SUPPLIERS
    # =========================================================

    @staticmethod
    def get_suppliers(db):

        cached = get_cache(
            AnalyticsService.SUPPLIER_CACHE_KEY
        )

        if cached is not None:
            return {
                "suppliers": cached
            }

        suppliers = (
            AnalyticsRepository
            .get_supplier_performance(db)
        )

        set_cache(
            AnalyticsService.SUPPLIER_CACHE_KEY,
            suppliers,
            AnalyticsService.DASHBOARD_TTL,
        )

        return {
            "suppliers": suppliers
        }

    # =========================================================
    # WAREHOUSES
    # =========================================================

    @staticmethod
    def get_warehouses(db):

        cached = get_cache(
            AnalyticsService.WAREHOUSE_CACHE_KEY
        )

        if cached is not None:
            return {
                "warehouses": cached
            }

        warehouses = (
            AnalyticsRepository
            .get_warehouse_analytics(db)
        )

        set_cache(
            AnalyticsService.WAREHOUSE_CACHE_KEY,
            warehouses,
            AnalyticsService.DASHBOARD_TTL,
        )

        return {
            "warehouses": warehouses
        }

    # =========================================================
    # CACHE INVALIDATION
    # =========================================================

    @staticmethod
    def invalidate_cache():

        delete_cache(
            AnalyticsService.DASHBOARD_CACHE_KEY
        )

        delete_cache(
            AnalyticsService.INVENTORY_CACHE_KEY
        )

        delete_cache(
            AnalyticsService.SUPPLIER_CACHE_KEY
        )

        delete_cache(
            AnalyticsService.WAREHOUSE_CACHE_KEY
        )