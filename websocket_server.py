import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed
from database import Database
from models import MessageStatus, MessageType, MessageCreate
from logger import logger


class WebSocketManager:
    def __init__(self, db: Database):
        self.db = db
        self.active_connections: Dict[int, WebSocketServerProtocol] = {}
        self.user_typing: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocketServerProtocol, user_id: int) -> None:
        self.active_connections[user_id] = websocket
        session = self.db.get_session()
        self.db.set_user_online(session, user_id, True)
        session.close()
        logger.info(f"User {user_id} connected")

    async def disconnect(self, user_id: int) -> None:
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        session = self.db.get_session()
        self.db.set_user_online(session, user_id, False)
        session.close()
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, user_id: int, message: dict) -> None:
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send(json.dumps(message))
            except ConnectionClosed:
                await self.disconnect(user_id)

    async def broadcast_typing(self, sender_id: int, recipient_id: int, is_typing: bool) -> None:
        message = {
            "action": "typing",
            "user_id": sender_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(recipient_id, message)

    async def send_message(self, sender_id: int, recipient_id: int, content: str, message_type: MessageType = MessageType.TEXT) -> None:
        session = self.db.get_session()
        db_message = self.db.create_message(session, sender_id, recipient_id, content, message_type)
        session.close()

        message = {
            "action": "message",
            "message_id": db_message.id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
            "message_type": message_type.value,
            "status": MessageStatus.SENT.value,
            "created_at": db_message.created_at.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }

        if recipient_id in self.active_connections:
            await self.send_personal_message(recipient_id, message)
        else:
            logger.info(f"User {recipient_id} is offline, message queued")

    async def send_read_receipt(self, message_id: int, reader_id: int) -> None:
        session = self.db.get_session()
        message = self.db.get_message_by_id(session, message_id)
        if message:
            self.db.update_message_status(session, message_id, MessageStatus.READ)
            receipt = {
                "action": "read_receipt",
                "message_id": message_id,
                "reader_id": reader_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.send_personal_message(message.sender_id, receipt)
        session.close()

    async def edit_message(self, message_id: int, new_content: str, user_id: int) -> None:
        session = self.db.get_session()
        message = self.db.get_message_by_id(session, message_id)
        if message and message.sender_id == user_id:
            self.db.edit_message(session, message_id, new_content)
            edit_notification = {
                "action": "message_edited",
                "message_id": message_id,
                "new_content": new_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.send_personal_message(message.recipient_id, edit_notification)
        session.close()

    async def delete_message(self, message_id: int, user_id: int) -> None:
        session = self.db.get_session()
        message = self.db.get_message_by_id(session, message_id)
        if message and message.sender_id == user_id:
            self.db.delete_message(session, message_id)
            delete_notification = {
                "action": "message_deleted",
                "message_id": message_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.send_personal_message(message.recipient_id, delete_notification)
        session.close()

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def get_online_users(self) -> list:
        return list(self.active_connections.keys())
