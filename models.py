from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    avatar: str = Field(default="😀")


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    is_online: bool
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    recipient_id: int
    content: str
    message_type: MessageType = MessageType.TEXT
    file_path: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    message_type: MessageType
    file_path: Optional[str] = None
    status: MessageStatus
    created_at: datetime
    edited_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatPreview(BaseModel):
    user_id: int
    username: str
    avatar: str
    is_online: bool
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0


class SearchUserRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50)


class TypingIndicator(BaseModel):
    user_id: int
    recipient_id: int
    is_typing: bool


class ReadReceipt(BaseModel):
    message_id: int
    reader_id: int


class MessageEdit(BaseModel):
    message_id: int
    new_content: str


class MessageDelete(BaseModel):
    message_id: int


class WebSocketMessage(BaseModel):
    action: str
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
