import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.purchase_order_service import PurchaseOrderService
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem


def test_generate_po_number():
    po_number = PurchaseOrderService._generate_po_number()

    assert po_number.startswith("PO-")
    assert len(po_number) > 3


def test_get_by_id_not_found():
    db = MagicMock()

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=None
    )

    with pytest.raises(Exception):
        PurchaseOrderService.get_by_id(
            db=db,
            purchase_order_id=999
        )


def test_get_all_empty():
    db = MagicMock()

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_all = MagicMock(
        return_value=([], 0)
    )

    result = PurchaseOrderService.get_all(
        db=db,
        page=1,
        page_size=10
    )

    assert result["items"] == []
    assert result["total"] == 0
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert result["total_pages"] == 0


def test_submit_only_draft():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-001",
        supplier_id=1,
        warehouse_id=1,
        status="APPROVED",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    with pytest.raises(Exception):
        PurchaseOrderService.submit_for_approval(
            db=db,
            purchase_order_id=1
        )


def test_submit_draft_purchase_order():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-002",
        supplier_id=1,
        warehouse_id=1,
        status="DRAFT",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    result = PurchaseOrderService.submit_for_approval(
        db=db,
        purchase_order_id=1
    )

    assert result.status == "PENDING_APPROVAL"
    db.commit.assert_called_once()


def test_approve_purchase_order():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-003",
        supplier_id=1,
        warehouse_id=1,
        status="PENDING_APPROVAL",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    result = PurchaseOrderService.approve(
        db=db,
        purchase_order_id=1,
        user_id=5
    )

    assert result.status == "APPROVED"
    assert result.approved_by == 5
    assert result.approved_at is not None
    db.commit.assert_called_once()


def test_approve_only_pending():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-004",
        supplier_id=1,
        warehouse_id=1,
        status="DRAFT",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    with pytest.raises(Exception):
        PurchaseOrderService.approve(
            db=db,
            purchase_order_id=1,
            user_id=5
        )


def test_reject_purchase_order():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-005",
        supplier_id=1,
        warehouse_id=1,
        status="PENDING_APPROVAL",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    result = PurchaseOrderService.reject(
        db=db,
        purchase_order_id=1
    )

    assert result.status == "REJECTED"
    db.commit.assert_called_once()


def test_cancel_purchase_order():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-006",
        supplier_id=1,
        warehouse_id=1,
        status="DRAFT",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    result = PurchaseOrderService.cancel(
        db=db,
        purchase_order_id=1
    )

    assert result.status == "CANCELLED"
    db.commit.assert_called_once()


def test_cannot_cancel_completed_order():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-007",
        supplier_id=1,
        warehouse_id=1,
        status="COMPLETED",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    with pytest.raises(Exception):
        PurchaseOrderService.cancel(
            db=db,
            purchase_order_id=1
        )


def test_mark_ordered():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-008",
        supplier_id=1,
        warehouse_id=1,
        status="APPROVED",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    result = PurchaseOrderService.mark_ordered(
        db=db,
        purchase_order_id=1
    )

    assert result.status == "ORDERED"
    db.commit.assert_called_once()


def test_mark_ordered_only_approved():
    db = MagicMock()

    po = PurchaseOrder(
        id=1,
        po_number="PO-TEST-009",
        supplier_id=1,
        warehouse_id=1,
        status="DRAFT",
        total_amount=100,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    with pytest.raises(Exception):
        PurchaseOrderService.mark_ordered(
            db=db,
            purchase_order_id=1
        )

def test_receive_purchase_order():
    db = MagicMock()

    po_item = PurchaseOrderItem(
        id=1,
        product_id=1,
        quantity=40,
        received_quantity=0,
        unit_price=100,
        total_price=4000,
    )

    po = PurchaseOrder(
        id=5,
        po_number="PO-TEST-RECEIVE",
        supplier_id=1,
        warehouse_id=1,
        status="ORDERED",
        total_amount=4000,
        created_by=1,
    )

    po.items = [po_item]

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    from app.services.inventory_service import InventoryService

    InventoryService.stock_in = MagicMock()

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=40
            )
        ]
    )

    result = PurchaseOrderService.receive(
        db=db,
        purchase_order_id=5,
        data=data,
        user_id=1
    )

    assert po_item.received_quantity == 40
    assert result.status == "RECEIVED"

    InventoryService.stock_in.assert_called_once()

    db.commit.assert_called_once()


def test_receive_partial_purchase_order():
    db = MagicMock()

    po_item = PurchaseOrderItem(
        id=1,
        product_id=1,
        quantity=100,
        received_quantity=0,
        unit_price=100,
        total_price=10000,
    )

    po = PurchaseOrder(
        id=6,
        po_number="PO-TEST-PARTIAL",
        supplier_id=1,
        warehouse_id=1,
        status="ORDERED",
        total_amount=10000,
        created_by=1,
    )

    po.items = [po_item]

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    from app.services.inventory_service import InventoryService

    InventoryService.stock_in = MagicMock()

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=40
            )
        ]
    )

    result = PurchaseOrderService.receive(
        db=db,
        purchase_order_id=6,
        data=data,
        user_id=1
    )

    assert po_item.received_quantity == 40
    assert result.status == "PARTIALLY_RECEIVED"

    InventoryService.stock_in.assert_called_once()


def test_receive_rejects_unknown_product():
    db = MagicMock()

    po_item = PurchaseOrderItem(
        id=1,
        product_id=1,
        quantity=40,
        received_quantity=0,
        unit_price=100,
        total_price=4000,
    )

    po = PurchaseOrder(
        id=7,
        po_number="PO-TEST-UNKNOWN",
        supplier_id=1,
        warehouse_id=1,
        status="ORDERED",
        total_amount=4000,
        created_by=1,
    )

    po.items = [po_item]

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=999,
                quantity=10
            )
        ]
    )

    with pytest.raises(Exception):
        PurchaseOrderService.receive(
            db=db,
            purchase_order_id=7,
            data=data,
            user_id=1
        )


def test_receive_rejects_excess_quantity():
    db = MagicMock()

    po_item = PurchaseOrderItem(
        id=1,
        product_id=1,
        quantity=40,
        received_quantity=0,
        unit_price=100,
        total_price=4000,
    )

    po = PurchaseOrder(
        id=8,
        po_number="PO-TEST-EXCESS",
        supplier_id=1,
        warehouse_id=1,
        status="ORDERED",
        total_amount=4000,
        created_by=1,
    )

    po.items = [po_item]

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=50
            )
        ]
    )

    with pytest.raises(Exception):
        PurchaseOrderService.receive(
            db=db,
            purchase_order_id=8,
            data=data,
            user_id=1
        )


def test_receive_rejects_invalid_status():
    db = MagicMock()

    po = PurchaseOrder(
        id=9,
        po_number="PO-TEST-STATUS",
        supplier_id=1,
        warehouse_id=1,
        status="DRAFT",
        total_amount=4000,
        created_by=1,
    )

    from app.repositories.purchase_order_repository import (
        PurchaseOrderRepository
    )

    PurchaseOrderRepository.get_by_id = MagicMock(
        return_value=po
    )

    data = SimpleNamespace(
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=10
            )
        ]
    )

    with pytest.raises(Exception):
        PurchaseOrderService.receive(
            db=db,
            purchase_order_id=9,
            data=data,
            user_id=1
        )