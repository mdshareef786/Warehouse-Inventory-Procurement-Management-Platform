def test_dashboard_requires_authentication(client):

    response = client.get(
        "/analytics/dashboard"
    )

    assert response.status_code in (
        401,
        403,
    )


def test_inventory_analytics_requires_authentication(client):

    response = client.get(
        "/analytics/inventory"
    )

    assert response.status_code in (
        401,
        403,
    )


def test_supplier_analytics_requires_authentication(client):

    response = client.get(
        "/analytics/suppliers"
    )

    assert response.status_code in (
        401,
        403,
    )


def test_warehouse_analytics_requires_authentication(client):

    response = client.get(
        "/analytics/warehouses"
    )

    assert response.status_code in (
        401,
        403,
    )