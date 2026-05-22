from fastapi import WebSocket
from typing import List

class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.active_connections = []
            print("--- ConnectionManager Initialized ---")
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WS Client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WS Client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        print(f"Broadcasting to {len(self.active_connections)} clients...")
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send to a client: {e}")

manager = ConnectionManager()
