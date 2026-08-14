from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_inventory_requires_authentication():
    response = client.get("/inventory")

    assert response.status_code in (401, 403)


def test_inventory_item_requires_authentication():
    response = client.get("/inventory/1/1")

    assert response.status_code in (401, 403)


def test_inventory_history_requires_authentication():
    response = client.get(
        "/inventory/history?page=1&page_size=10"
    )

    assert response.status_code in (401, 403)


def test_stock_in_requires_authentication():
    response = client.post(
        "/inventory/stock-in",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 10,
            "reason": "Test stock in"
        }
    )

    assert response.status_code in (401, 403)


def test_stock_out_requires_authentication():
    response = client.post(
        "/inventory/stock-out",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 10,
            "reason": "Test stock out"
        }
    )

    assert response.status_code in (401, 403)


def test_reserve_requires_authentication():
    response = client.post(
        "/inventory/reserve",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 10,
            "reason": "Test reservation"
        }
    )

    assert response.status_code in (401, 403)


def test_release_requires_authentication():
    response = client.post(
        "/inventory/release",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 10,
            "reason": "Test release"
        }
    )

    assert response.status_code in (401, 403)


def test_damage_requires_authentication():
    response = client.post(
        "/inventory/damage",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 5,
            "reason": "Test damage"
        }
    )

    assert response.status_code in (401, 403)


def test_adjust_requires_authentication():
    response = client.post(
        "/inventory/adjust",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "quantity": 100,
            "reason": "Test adjustment"
        }
    )

    assert response.status_code in (401, 403)


def test_reconcile_requires_authentication():
    response = client.post(
        "/inventory/reconcile",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "physical_quantity": 100,
            "reason": "Physical stock verification"
        }
    )

    assert response.status_code in (401, 403)