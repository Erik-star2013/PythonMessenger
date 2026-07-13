import asyncio
import json
import websockets
from typing import Callable, Optional, Any
from datetime import datetime
from logger import logger
from websockets.exceptions import ConnectionClosed


class WebSocketClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.websocket = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2.0
        self.on_message_callbacks = []
        self.on_disconnect_callbacks = []

    async def connect(self) -> bool:
        try:
            connection_url = f"{self.url}/{self.token}"
            self.websocket = await websockets.connect(connection_url)
            self.is_connected = True
            self.reconnect_attempts = 0
            logger.info(f"WebSocket connected")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            return False

    async def disconnect(self) -> None:
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        self.is_connected = False
        logger.info("WebSocket disconnected")

    async def send(self, action: str, data: dict) -> bool:
        if not self.is_connected or not self.websocket:
            logger.warning("Cannot send message: WebSocket not connected")
            return False
        
        try:
            message = {
                "action": action,
                **data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"WebSocket send error: {str(e)}")
            self.is_connected = False
            return False

    async def receive_loop(self) -> None:
        try:
            while self.is_connected:
                try:
                    message_text = await self.websocket.recv()
                    message = json.loads(message_text)
                    
                    for callback in self.on_message_callbacks:
                        try:
                            callback(message)
                        except Exception as e:
                            logger.error(f"Callback error: {str(e)}")
                
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received from WebSocket")
                except ConnectionClosed:
                    break
                except Exception as e:
                    logger.error(f"Receive error: {str(e)}")
                    break
        
        except Exception as e:
            logger.error(f"Receive loop error: {str(e)}")
        
        finally:
            self.is_connected = False
            for callback in self.on_disconnect_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Disconnect callback error: {str(e)}")

    def on_message(self, callback: Callable) -> None:
        self.on_message_callbacks.append(callback)

    def on_disconnect(self, callback: Callable) -> None:
        self.on_disconnect_callbacks.append(callback)

    async def send_message(self, recipient_id: int, content: str) -> bool:
        return await self.send("message", {
            "recipient_id": recipient_id,
            "content": content
        })

    async def send_typing(self, recipient_id: int, is_typing: bool) -> bool:
        return await self.send("typing", {
            "recipient_id": recipient_id,
            "is_typing": is_typing
        })

    async def send_read_receipt(self, message_id: int) -> bool:
        return await self.send("read_receipt", {
            "message_id": message_id
        })

    async def send_edit_message(self, message_id: int, new_content: str) -> bool:
        return await self.send("edit_message", {
            "message_id": message_id,
            "new_content": new_content
        })

    async def send_delete_message(self, message_id: int) -> bool:
        return await self.send("delete_message", {
            "message_id": message_id
        })
