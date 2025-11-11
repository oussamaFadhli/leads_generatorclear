from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for client_id in list(self.active_connections.keys()):
            for connection in list(self.active_connections[client_id]):
                try:
                    await connection.send_text(message)
                except RuntimeError:
                    # Handle cases where the WebSocket might have closed unexpectedly
                    self.active_connections[client_id].remove(connection)
                    if not self.active_connections[client_id]:
                        del self.active_connections[client_id]

    async def broadcast_to_client(self, client_id: str, message: str):
        if client_id in self.active_connections:
            for connection in list(self.active_connections[client_id]):
                try:
                    await connection.send_text(message)
                except RuntimeError:
                    self.active_connections[client_id].remove(connection)
                    if not self.active_connections[client_id]:
                        del self.active_connections[client_id]

websocket_manager = WebSocketManager()
