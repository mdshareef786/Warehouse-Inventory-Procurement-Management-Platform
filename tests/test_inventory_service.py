from unittest.mock import MagicMock, patch

import pytest

from app.models.inventory import Inventory
from app.services.inventory_service import InventoryService


# =========================================================
# HELPERS
# =========================================================

def create_inventory(
    available=100,
    reserved=20,
    damaged=10,
):
    return Inventory(
        id=1,
        product_id=1,
        warehouse_id=1,
        available_quantity=available,
        reserved_quantity=reserved,
        damaged_quantity=damaged,
    )


def create_db():
    return MagicMock()


# =========================================================
# STOCK IN
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_stock_in(
    mock_get,
    mock_create,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.stock_in(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=40,
            user_id=1,
            reason="Test stock in",
        )

    assert result.available_quantity == 140
    assert result.reserved_quantity == 20
    assert result.damaged_quantity == 10

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once_with(
        product_id=1,
        warehouse_id=1,
    )


# =========================================================
# STOCK OUT
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_stock_out(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.stock_out(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=30,
            user_id=1,
            reason="Customer order",
        )

    assert result.available_quantity == 70

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# STOCK OUT - INSUFFICIENT STOCK
# =========================================================

@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_stock_out_insufficient_stock(
    mock_get,
):
    db = create_db()

    inventory = create_inventory(
        available=10,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):

        with pytest.raises(Exception) as exc:
            InventoryService.stock_out(
                db=db,
                product_id=1,
                warehouse_id=1,
                quantity=50,
                user_id=1,
                reason="Too much stock",
            )

    assert "Insufficient" in str(exc.value)


# =========================================================
# RESERVE
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_reserve_inventory(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.reserve(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=30,
            user_id=1,
            reason="Customer reservation",
        )

    assert result.available_quantity == 70
    assert result.reserved_quantity == 50

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# RELEASE
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_release_inventory(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=70,
        reserved=50,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.release(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=20,
            user_id=1,
            reason="Customer order cancelled",
        )

    assert result.available_quantity == 90
    assert result.reserved_quantity == 30

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# RELEASE - INSUFFICIENT RESERVED STOCK
# =========================================================

@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_release_insufficient_reserved_stock(
    mock_get,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=5,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):

        with pytest.raises(Exception) as exc:
            InventoryService.release(
                db=db,
                product_id=1,
                warehouse_id=1,
                quantity=20,
                user_id=1,
                reason="Invalid release",
            )

    assert "reserved" in str(exc.value).lower()


# =========================================================
# DAMAGE
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_damage_inventory(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.damage(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=15,
            user_id=1,
            reason="Damaged during handling",
        )

    assert result.available_quantity == 85
    assert result.damaged_quantity == 25

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# ADJUST
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_adjust_inventory(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.adjust(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=150,
            user_id=1,
            reason="Physical stock adjustment",
        )

    assert result.available_quantity == 150

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# RECONCILIATION
# =========================================================

@patch(
    "app.services.inventory_service.AlertService.check_inventory_alert"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.invalidate_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.create_transaction"
)
@patch(
    "app.services.inventory_service.InventoryRepository.update"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_reconcile_inventory(
    mock_get,
    mock_update,
    mock_transaction,
    mock_cache,
    mock_alert,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ):
        result = InventoryService.reconcile(
            db=db,
            product_id=1,
            warehouse_id=1,
            physical_quantity=180,
            user_id=1,
            reason="Monthly physical verification",
        )

    # 180 physical
    # - 20 reserved
    # - 10 damaged
    # = 150 available

    assert result.available_quantity == 150

    mock_update.assert_called_once()
    mock_transaction.assert_called_once()
    mock_alert.assert_called_once()
    mock_cache.assert_called_once()


# =========================================================
# RECONCILIATION - NO CHANGE
# =========================================================

@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_reconcile_no_change(
    mock_get,
):
    db = create_db()

    inventory = create_inventory(
        available=100,
        reserved=20,
        damaged=10,
    )

    mock_get.return_value = inventory

    with patch.object(
        InventoryService,
        "_validate_product"
    ), patch.object(
        InventoryService,
        "_validate_warehouse"
    ), patch(
        "app.services.inventory_service.InventoryRepository.update"
    ) as mock_update:

        result = InventoryService.reconcile(
            db=db,
            product_id=1,
            warehouse_id=1,
            physical_quantity=130,
            user_id=1,
            reason="No difference",
        )

    assert result.available_quantity == 100
    mock_update.assert_not_called()


# =========================================================
# VALIDATION
# =========================================================

def test_stock_in_rejects_zero_quantity():
    db = create_db()

    with pytest.raises(ValueError) as exc:
        InventoryService.stock_in(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=0,
            user_id=1,
        )

    assert "greater than zero" in str(exc.value)


def test_stock_out_rejects_negative_quantity():
    db = create_db()

    with pytest.raises(ValueError):
        InventoryService.stock_out(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=-5,
            user_id=1,
        )


def test_reserve_rejects_zero_quantity():
    db = create_db()

    with pytest.raises(ValueError):
        InventoryService.reserve(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=0,
            user_id=1,
        )


def test_damage_rejects_zero_quantity():
    db = create_db()

    with pytest.raises(ValueError):
        InventoryService.damage(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=0,
            user_id=1,
            reason="Invalid damage",
        )


def test_adjust_rejects_negative_quantity():
    db = create_db()

    with pytest.raises(ValueError):
        InventoryService.adjust(
            db=db,
            product_id=1,
            warehouse_id=1,
            quantity=-1,
            user_id=1,
            reason="Invalid adjustment",
        )


def test_reconcile_rejects_negative_quantity():
    db = create_db()

    with pytest.raises(ValueError):
        InventoryService.reconcile(
            db=db,
            product_id=1,
            warehouse_id=1,
            physical_quantity=-10,
            user_id=1,
            reason="Invalid reconciliation",
        )


# =========================================================
# INVENTORY CACHE
# =========================================================

@patch(
    "app.services.inventory_service.InventoryCacheService.set_inventory"
)
@patch(
    "app.services.inventory_service.InventoryCacheService.get_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_get_inventory_item_cache_miss(
    mock_get_repository,
    mock_get_cache,
    mock_set_cache,
):
    db = create_db()

    inventory = create_inventory()

    mock_get_cache.return_value = None
    mock_get_repository.return_value = inventory

    result = InventoryService.get_inventory_item(
        db=db,
        product_id=1,
        warehouse_id=1,
    )

    assert result == inventory

    mock_get_repository.assert_called_once_with(
        db=db,
        product_id=1,
        warehouse_id=1,
    )

    mock_set_cache.assert_called_once()


@patch(
    "app.services.inventory_service.InventoryCacheService.get_inventory"
)
@patch(
    "app.services.inventory_service.InventoryRepository.get_by_product_and_warehouse"
)
def test_get_inventory_item_cache_hit(
    mock_get_repository,
    mock_get_cache,
):
    db = create_db()

    cached_inventory = {
        "id": 1,
        "product_id": 1,
        "warehouse_id": 1,
        "available_quantity": 100,
    }

    mock_get_cache.return_value = cached_inventory

    result = InventoryService.get_inventory_item(
        db=db,
        product_id=1,
        warehouse_id=1,
    )

    assert result == cached_inventory

    # PostgreSQL should NOT be queried on cache hit.
    mock_get_repository.assert_not_called()