from app.core.redis import (
    set_cache,
    get_cache,
    delete_cache,
    clear_cache_pattern,
)


class InventoryCacheService:

    INVENTORY_TTL = 300

    @staticmethod
    def inventory_key(
        product_id: int,
        warehouse_id: int,
    ):
        return (
            f"inventory:"
            f"{product_id}:"
            f"{warehouse_id}"
        )

    @staticmethod
    def get_inventory(
        product_id: int,
        warehouse_id: int,
    ):
        key = InventoryCacheService.inventory_key(
            product_id,
            warehouse_id,
        )

        return get_cache(key)

    @staticmethod
    def set_inventory(
        product_id: int,
        warehouse_id: int,
        inventory,
    ):
        key = InventoryCacheService.inventory_key(
            product_id,
            warehouse_id,
        )

        data = {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "warehouse_id": inventory.warehouse_id,
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
            "damaged_quantity": inventory.damaged_quantity,
            "last_updated": (
                inventory.last_updated.isoformat()
                if inventory.last_updated
                else None
            ),
        }

        set_cache(
            key,
            data,
            InventoryCacheService.INVENTORY_TTL,
        )

    @staticmethod
    def invalidate_inventory(
        product_id: int,
        warehouse_id: int,
    ):
        key = InventoryCacheService.inventory_key(
            product_id,
            warehouse_id,
        )

        delete_cache(key)

    @staticmethod
    def invalidate_all():
        clear_cache_pattern(
            "inventory:*"
        )