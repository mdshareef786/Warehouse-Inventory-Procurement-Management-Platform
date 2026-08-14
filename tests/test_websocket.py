def test_alert_websocket(client):

    with client.websocket_connect(
        "/ws/alerts"
    ) as websocket:

        message = websocket.receive_json()

        assert message["type"] == "connection"

        assert (
            message["message"]
            == "WebSocket connection established successfully"
        )