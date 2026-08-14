import asyncio
import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()
        self.queues: dict[WebSocket, asyncio.Queue] = {}

    async def connect(
        self,
        websocket: WebSocket
    ):
        await websocket.accept()

        self.active_connections.add(websocket)

        self.queues[websocket] = asyncio.Queue()

    def disconnect(
        self,
        websocket: WebSocket
    ):
        self.active_connections.discard(
            websocket
        )

        self.queues.pop(
            websocket,
            None
        )

    async def send_personal_message(
        self,
        websocket: WebSocket,
        message: dict
    ):
        await websocket.send_json(
            message
        )

    async def broadcast(
        self,
        message: dict
    ):
        disconnected = []

        for websocket in list(
            self.active_connections
        ):
            try:
                await websocket.send_json(
                    message
                )
            except Exception:
                disconnected.append(
                    websocket
                )

        for websocket in disconnected:
            self.disconnect(
                websocket
            )

    def publish(
        self,
        message: dict
    ):
        """
        Thread-safe synchronous publisher.

        This can be called from normal
        synchronous SQLAlchemy services.
        """

        payload = json.loads(
            json.dumps(
                message,
                default=str
            )
        )

        for websocket, queue in list(
            self.queues.items()
        ):
            try:
                queue.put_nowait(
                    payload
                )
            except Exception:
                self.disconnect(
                    websocket
                )


manager = ConnectionManager()