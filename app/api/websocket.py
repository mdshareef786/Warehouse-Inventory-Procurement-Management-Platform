import asyncio

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.core.websocket_manager import manager


router = APIRouter(
    tags=["WebSocket"]
)


@router.websocket(
    "/ws/alerts"
)
async def websocket_alerts(
    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        await manager.send_personal_message(
            websocket,
            {
                "type": "connection",
                "message": (
                    "WebSocket connection "
                    "established successfully"
                )
            }
        )

        queue = manager.queues[
            websocket
        ]

        while True:

            try:

                message = await asyncio.wait_for(
                    queue.get(),
                    timeout=30
                )

                await websocket.send_json(
                    message
                )

            except asyncio.TimeoutError:

                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "message": "connection_alive"
                    }
                )

    except WebSocketDisconnect:

        manager.disconnect(
            websocket
        )

    except Exception:

        manager.disconnect(
            websocket
        )