import asyncio
import json
from typing import List

from fastapi import APIRouter, WebSocket

from ..api_tags import WEBSOCKET
from ..models.api import Event, Stats

websocket_router = APIRouter(
    prefix="/websocket",
    tags=[WEBSOCKET]
)

clients: List[WebSocket] = []

async def broadcast_event(event: Event):
    if len(clients) == 0: return

    text = json.dumps(event.encode())

    for client in clients:
        asyncio.create_task(client.send_text(text))

@websocket_router.websocket("/", name="Вебсокет")
async def send_events(websocket: WebSocket):
    await websocket.accept()

    clients.append(websocket)

    await broadcast_event(
        Event(
            updateStats=Stats(
                online=len(clients)
            )
        )
    )

    while True:
        try:
            await websocket.receive_text()
        except:
            clients.remove(websocket)

            await broadcast_event(
                Event(
                    updateStats=Stats(
                        online=len(clients)
                    )
                )
            )

            return