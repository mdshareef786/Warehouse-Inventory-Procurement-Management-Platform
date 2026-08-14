import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.stock_transfer import (
    StockTransfer,
    StockTransferItem,
)

from app.services.stock_transfer_service import (
    StockTransferService,
)

from app.exceptions.custom_exceptions import (
    TransferNotFoundException,
    InvalidTransferException,
    TransferAlreadyApprovedException,
    TransferAlreadyRejectedException,
    TransferNotReadyException,
    InsufficientStockException,
    SameWarehouseTransferException,
)


def make_item(
    product_id=1,
    quantity=20,
    received_quantity=0,
):
    return StockTransferItem(
        id=1,
        product_id=product_id,
        quantity=quantity,
        received_quantity=received_quantity,
    )


def make_transfer(
    transfer_id=1,
    status="REQUESTED",
):
    transfer = StockTransfer(
        id=transfer_id,
        transfer_number="TR-TEST-001",
        source_warehouse_id=1,
        destination_warehouse_id=2,
        requested_by=1,
        status=status,
    )

    transfer.items = [
        make_item()
    ]

    return transfer


# =========================================================
# TRANSFER NUMBER
# =========================================================


def test_generate_transfer_number():
    number = (
        StockTransferService
        ._generate_transfer_number()
    )

    assert number.startswith("TR-")
    assert len(number) > 3


# =========================================================
# GET BY ID
# =========================================================


def test_get_by_id_not_found(monkeypatch):

    db = MagicMock()

    monkeypatch.setattr(
        "app.repositories.stock_transfer_repository.StockTransferRepository.get_by_id",
        lambda db, transfer_id: None,
    )

    with pytest.raises(
        TransferNotFoundException
    ):
        StockTransferService.get_by_id(
            db,
            999
        )


def test_get_by_id():

    db = MagicMock()

    transfer = make_transfer()

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        "app.repositories.stock_transfer_repository.StockTransferRepository.get_by_id",
        lambda db, transfer_id: transfer,
    )

    result = StockTransferService.get_by_id(
        db,
        1
    )

    assert result == transfer

    monkeypatch.undo()


# =========================================================
# GET ALL
# =========================================================


def test_get_all_empty():

    db = MagicMock()

    repository = MagicMock()

    repository.get_all.return_value = (
        [],
        0
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        "app.services.stock_transfer_service.StockTransferRepository",
        repository
    )

    result = StockTransferService.get_all(
        db=db,
        page=1,
        page_size=10
    )

    assert result["items"] == []
    assert result["total"] == 0
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert result["total_pages"] == 0

    monkeypatch.undo()


# =========================================================
# CREATE VALIDATION
# =========================================================


def test_create_rejects_same_warehouse():

    db = MagicMock()

    data = SimpleNamespace(
        source_warehouse_id=1,
        destination_warehouse_id=1,
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=10
            )
        ]
    )

    with pytest.raises(
        SameWarehouseTransferException
    ):
        StockTransferService.create(
            db=db,
            data=data,
            user_id=1
        )


def test_create_rejects_empty_items():

    db = MagicMock()

    data = SimpleNamespace(
        source_warehouse_id=1,
        destination_warehouse_id=2,
        items=[]
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "_validate_warehouse",
        lambda db, warehouse_id: True,
    )

    with pytest.raises(
        InvalidTransferException
    ):
        StockTransferService.create(
            db=db,
            data=data,
            user_id=1
        )

    monkeypatch.undo()


def test_create_rejects_duplicate_products():

    db = MagicMock()

    data = SimpleNamespace(
        source_warehouse_id=1,
        destination_warehouse_id=2,
        items=[
            SimpleNamespace(
                product_id=1,
                quantity=10
            ),
            SimpleNamespace(
                product_id=1,
                quantity=20
            ),
        ]
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "_validate_warehouse",
        lambda db, warehouse_id: True,
    )

    monkeypatch.setattr(
        StockTransferService,
        "_validate_product",
        lambda db, product_id: True,
    )

    with pytest.raises(
        InvalidTransferException
    ):
        StockTransferService.create(
            db=db,
            data=data,
            user_id=1
        )

    monkeypatch.undo()


# =========================================================
# APPROVE
# =========================================================


def test_approve_transfer():

    db = MagicMock()

    transfer = make_transfer(
        status="REQUESTED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    inventory = SimpleNamespace(
        available_quantity=100
    )

    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory_item",
        lambda **kwargs: inventory,
    )

    result = StockTransferService.approve(
        db=db,
        transfer_id=1,
        user_id=5
    )

    assert result.status == "APPROVED"
    assert result.approved_by == 5
    assert result.approved_at is not None

    db.commit.assert_called_once()

    monkeypatch.undo()


def test_approve_already_approved():

    db = MagicMock()

    transfer = make_transfer(
        status="APPROVED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    with pytest.raises(
        TransferAlreadyApprovedException
    ):
        StockTransferService.approve(
            db=db,
            transfer_id=1,
            user_id=5
        )

    monkeypatch.undo()


def test_approve_insufficient_stock():

    db = MagicMock()

    transfer = make_transfer(
        status="REQUESTED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    inventory = SimpleNamespace(
        available_quantity=5
    )

    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.get_inventory_item",
        lambda **kwargs: inventory,
    )

    with pytest.raises(
        InsufficientStockException
    ):
        StockTransferService.approve(
            db=db,
            transfer_id=1,
            user_id=5
        )

    monkeypatch.undo()


# =========================================================
# REJECT
# =========================================================


def test_reject_transfer():

    db = MagicMock()

    transfer = make_transfer(
        status="REQUESTED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    result = StockTransferService.reject(
        db=db,
        transfer_id=1
    )

    assert result.status == "REJECTED"

    db.commit.assert_called_once()

    monkeypatch.undo()


def test_reject_already_rejected():

    db = MagicMock()

    transfer = make_transfer(
        status="REJECTED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    with pytest.raises(
        TransferAlreadyRejectedException
    ):
        StockTransferService.reject(
            db=db,
            transfer_id=1
        )

    monkeypatch.undo()


# =========================================================
# DISPATCH
# =========================================================


def test_dispatch_transfer():

    db = MagicMock()

    transfer = make_transfer(
        status="APPROVED"
    )

    stock_out = MagicMock()

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.stock_out",
        stock_out
    )

    result = StockTransferService.dispatch(
        db=db,
        transfer_id=1,
        user_id=5
    )

    assert result.status == "IN_TRANSIT"

    stock_out.assert_called_once()

    db.commit.assert_called_once()

    monkeypatch.undo()


def test_dispatch_requires_approved_status():

    db = MagicMock()

    transfer = make_transfer(
        status="REQUESTED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    with pytest.raises(
        TransferNotReadyException
    ):
        StockTransferService.dispatch(
            db=db,
            transfer_id=1,
            user_id=5
        )

    monkeypatch.undo()


# =========================================================
# RECEIVE
# =========================================================


def test_receive_transfer():

    db = MagicMock()

    transfer = make_transfer(
        status="IN_TRANSIT"
    )

    stock_in = MagicMock()

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    monkeypatch.setattr(
        "app.services.inventory_service.InventoryService.stock_in",
        stock_in
    )

    result = StockTransferService.receive(
        db=db,
        transfer_id=1,
        user_id=5
    )

    assert result.status == "RECEIVED"
    assert transfer.items[0].received_quantity == 20
    assert result.received_at is not None

    stock_in.assert_called_once()

    db.commit.assert_called_once()

    monkeypatch.undo()


def test_receive_requires_in_transit_status():

    db = MagicMock()

    transfer = make_transfer(
        status="APPROVED"
    )

    monkeypatch = pytest.MonkeyPatch()

    monkeypatch.setattr(
        StockTransferService,
        "get_by_id",
        lambda db, transfer_id: transfer,
    )

    with pytest.raises(
        TransferNotReadyException
    ):
        StockTransferService.receive(
            db=db,
            transfer_id=1,
            user_id=5
        )

    monkeypatch.undo()