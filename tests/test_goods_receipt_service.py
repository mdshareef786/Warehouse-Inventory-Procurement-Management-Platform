import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.goods_receipt import (
    GoodsReceipt,
    GoodsReceiptItem,
)
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
)

from app.services.goods_receipt_service import (
    GoodsReceiptService,
)

from app.exceptions.custom_exceptions import (
    PurchaseOrderNotFoundException,
    InvalidPurchaseOrderStatusException,
    InvalidPurchaseOrderItemException,
    InvalidPurchaseOrderReceiveException,
)


# =========================================================
# HELPERS
# =========================================================

def make_po(
    po_id=1,
    status="ORDERED",
    quantity=40,
    received_quantity=0,
):
    po_item = PurchaseOrderItem(
        id=1,
        product_id=1,
        quantity=quantity,
        received_quantity=received_quantity,
        unit_price=100,
        total_price=quantity * 100,
    )

    po = PurchaseOrder(
        id=po_id,
        po_number=f"PO-TEST-{po_id}",
        supplier_id=1,
        warehouse_id=1,
        status=status,
        total_amount=quantity * 100,
        created_by=1,
    )

    po.items = [po_item]

    return po


def make_data(
    product_id=1,
    quantity=10,
):
    return SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=product_id,
                quantity=quantity,
            )
        ]
    )


# =========================================================
# RECEIPT NUMBER
# =========================================================

def test_generate_receipt_number():

    number = (
        GoodsReceiptService
        ._generate_receipt_number()
    )

    assert number.startswith("GR-")
    assert len(number) > 3


# =========================================================
# GET BY ID
# =========================================================

def test_get_by_id_not_found(monkeypatch):

    db = MagicMock()

    repository = MagicMock()
    repository.get_by_id.return_value = None

    monkeypatch.setattr(
        "app.services.goods_receipt_service.GoodsReceiptRepository",
        repository,
    )

    with pytest.raises(
        ValueError,
        match="Goods receipt not found",
    ):
        GoodsReceiptService.get_by_id(
            db=db,
            receipt_id=999,
        )


def test_get_by_id(monkeypatch):

    db = MagicMock()

    receipt = GoodsReceipt(
        id=1,
        receipt_number="GR-TEST-001",
        purchase_order_id=1,
        warehouse_id=1,
        received_by=1,
        total_quantity=10,
        status="RECEIVED",
    )

    repository = MagicMock()
    repository.get_by_id.return_value = receipt

    monkeypatch.setattr(
        "app.services.goods_receipt_service.GoodsReceiptRepository",
        repository,
    )

    result = GoodsReceiptService.get_by_id(
        db=db,
        receipt_id=1,
    )

    assert result == receipt

    repository.get_by_id.assert_called_once_with(
        db,
        1,
    )


# =========================================================
# GET ALL
# =========================================================

def test_get_all_empty(monkeypatch):

    db = MagicMock()

    repository = MagicMock()

    repository.get_all.return_value = (
        [],
        0,
    )

    monkeypatch.setattr(
        "app.services.goods_receipt_service.GoodsReceiptRepository",
        repository,
    )

    result = GoodsReceiptService.get_all(
        db=db,
        page=1,
        page_size=10,
    )

    assert result["items"] == []
    assert result["total"] == 0
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert result["total_pages"] == 0

    repository.get_all.assert_called_once()


def test_get_all_with_results(monkeypatch):

    db = MagicMock()

    receipt = GoodsReceipt(
        id=1,
        receipt_number="GR-TEST-001",
        purchase_order_id=1,
        warehouse_id=1,
        received_by=1,
        total_quantity=40,
        status="RECEIVED",
    )

    repository = MagicMock()

    repository.get_all.return_value = (
        [receipt],
        11,
    )

    monkeypatch.setattr(
        "app.services.goods_receipt_service.GoodsReceiptRepository",
        repository,
    )

    result = GoodsReceiptService.get_all(
        db=db,
        page=2,
        page_size=10,
        purchase_order_id=1,
        warehouse_id=1,
    )

    assert result["items"] == [receipt]
    assert result["total"] == 11
    assert result["page"] == 2
    assert result["page_size"] == 10
    assert result["total_pages"] == 2

    repository.get_all.assert_called_once_with(
        db=db,
        page=2,
        page_size=10,
        purchase_order_id=1,
        warehouse_id=1,
    )


# =========================================================
# CREATE - SUCCESS
# =========================================================

def test_create_goods_receipt(monkeypatch):

    db = MagicMock()

    po = make_po(
        po_id=5,
        status="ORDERED",
        quantity=40,
        received_quantity=0,
    )

    db.query.return_value.filter.return_value.first.return_value = po

    stock_in = MagicMock()

    monkeypatch.setattr(
        "app.services.goods_receipt_service.InventoryService.stock_in",
        stock_in,
    )

    result = GoodsReceiptService.create(
        db=db,
        purchase_order_id=5,
        data=make_data(
            product_id=1,
            quantity=40,
        ),
        user_id=1,
    )

    assert result.receipt_number.startswith("GR-")
    assert result.purchase_order_id == 5
    assert result.warehouse_id == 1
    assert result.received_by == 1
    assert result.total_quantity == 40
    assert result.status == "RECEIVED"

    assert po.items[0].received_quantity == 40
    assert po.status == "RECEIVED"

    stock_in.assert_called_once()

    db.add.assert_called_once_with(result)
    db.flush.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


# =========================================================
# CREATE - PARTIAL RECEIPT
# =========================================================

def test_create_partial_goods_receipt(monkeypatch):

    db = MagicMock()

    po = make_po(
        po_id=5,
        status="ORDERED",
        quantity=100,
        received_quantity=0,
    )

    db.query.return_value.filter.return_value.first.return_value = po

    stock_in = MagicMock()

    monkeypatch.setattr(
        "app.services.goods_receipt_service.InventoryService.stock_in",
        stock_in,
    )

    result = GoodsReceiptService.create(
        db=db,
        purchase_order_id=5,
        data=make_data(
            product_id=1,
            quantity=40,
        ),
        user_id=1,
    )

    assert result.total_quantity == 40
    assert result.status == "RECEIVED"

    assert po.items[0].received_quantity == 40
    assert po.status == "PARTIALLY_RECEIVED"

    stock_in.assert_called_once()


# =========================================================
# CREATE - PURCHASE ORDER NOT FOUND
# =========================================================

def test_create_purchase_order_not_found():

    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(
        PurchaseOrderNotFoundException
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=999,
            data=make_data(),
            user_id=1,
        )


# =========================================================
# CREATE - INVALID PO STATUS
# =========================================================

@pytest.mark.parametrize(
    "status",
    [
        "DRAFT",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
        "CANCELLED",
        "RECEIVED",
    ],
)
def test_create_invalid_purchase_order_status(status):

    db = MagicMock()

    po = make_po(
        status=status,
    )

    db.query.return_value.filter.return_value.first.return_value = po

    with pytest.raises(
        InvalidPurchaseOrderStatusException
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=1,
            data=make_data(),
            user_id=1,
        )


# =========================================================
# CREATE - DUPLICATE PRODUCTS
# =========================================================

def test_create_rejects_duplicate_products():

    db = MagicMock()

    po = make_po()

    db.query.return_value.filter.return_value.first.return_value = po

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=10,
            ),
            SimpleNamespace(
                product_id=1,
                quantity=20,
            ),
        ]
    )

    with pytest.raises(
        InvalidPurchaseOrderItemException
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=1,
            data=data,
            user_id=1,
        )


# =========================================================
# CREATE - PRODUCT NOT IN PO
# =========================================================

def test_create_rejects_product_not_in_purchase_order():

    db = MagicMock()

    po = make_po()

    db.query.return_value.filter.return_value.first.return_value = po

    data = make_data(
        product_id=999,
        quantity=10,
    )

    with pytest.raises(
        InvalidPurchaseOrderItemException
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=1,
            data=data,
            user_id=1,
        )


# =========================================================
# CREATE - EXCESS QUANTITY
# =========================================================

def test_create_rejects_excess_quantity():

    db = MagicMock()

    po = make_po(
        quantity=40,
        received_quantity=30,
    )

    db.query.return_value.filter.return_value.first.return_value = po

    data = make_data(
        product_id=1,
        quantity=20,
    )

    with pytest.raises(
        InvalidPurchaseOrderReceiveException
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=1,
            data=data,
            user_id=1,
        )


# =========================================================
# CREATE - ATOMIC ROLLBACK
# =========================================================

def test_create_rolls_back_when_inventory_update_fails(
    monkeypatch,
):

    db = MagicMock()

    po = make_po(
        quantity=40,
        received_quantity=0,
    )

    db.query.return_value.filter.return_value.first.return_value = po

    stock_in = MagicMock(
        side_effect=Exception(
            "Inventory update failed"
        )
    )

    monkeypatch.setattr(
        "app.services.goods_receipt_service.InventoryService.stock_in",
        stock_in,
    )

    with pytest.raises(
        Exception,
        match="Inventory update failed",
    ):
        GoodsReceiptService.create(
            db=db,
            purchase_order_id=1,
            data=make_data(
                quantity=10,
            ),
            user_id=1,
        )

    db.rollback.assert_called_once()

    stock_in.assert_called_once()