def test_root_endpoint(client):

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "message" in data

    assert (
        data["message"]
        == "Warehouse Inventory & Procurement API Running Successfully"
    )