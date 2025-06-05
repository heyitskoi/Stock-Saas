from typing import Dict, Set
from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

class InventoryWSManager:
    def __init__(self) -> None:
        self.connections: Dict[int, Set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, tenant_id: int) -> None:
        await websocket.accept()
        self.connections[tenant_id].add(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: int) -> None:
        self.connections[tenant_id].discard(websocket)
        if not self.connections[tenant_id]:
            self.connections.pop(tenant_id, None)

    async def broadcast(self, tenant_id: int, data: dict) -> None:
        for ws in list(self.connections.get(tenant_id, [])):
            try:
                await ws.send_json(data)
            except WebSocketDisconnect:
                self.disconnect(ws, tenant_id)
            except Exception:
                self.disconnect(ws, tenant_id)
