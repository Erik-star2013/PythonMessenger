import os
from typing import Final

DATABASE_URL: Final[str] = "sqlite:///./messenger.db"
DATABASE_PATH: Final[str] = "messenger.db"

SERVER_HOST: Final[str] = "127.0.0.1"
SERVER_PORT: Final[int] = 8000
WS_PORT: Final[int] = 8001
WS_URL: Final[str] = f"ws://{SERVER_HOST}:{WS_PORT}"

MAX_MESSAGE_LENGTH: Final[int] = 5000
MAX_FILE_SIZE: Final[int] = 50 * 1024 * 1024
ALLOWED_FILE_EXTENSIONS: Final[set] = {
    "jpg", "jpeg", "png", "gif", "pdf", "doc", "docx",
    "txt", "zip", "rar", "mp3", "mp4", "webm"
}

LOG_LEVEL: Final[str] = "INFO"
LOG_FILE: Final[str] = "messenger.log"

TYPING_INDICATOR_TIMEOUT: Final[float] = 3.0
RECONNECT_ATTEMPTS: Final[int] = 5
RECONNECT_DELAY: Final[float] = 2.0

AVATARS: Final[list] = [
    "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂",
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼",
    "🐨", "🐯", "🦁", "🐮", "🐷", "🐽", "🐸", "🐵",
    "🚀", "🎮", "🎯", "🎨", "🎭", "🎪", "🎬", "🎤",
    "⚡", "💎", "🌟", "🔥", "💧", "🌈", "☀️", "🌙"
]
