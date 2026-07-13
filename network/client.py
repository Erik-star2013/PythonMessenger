import httpx
from typing import Optional, List, Dict, Any
from config import SERVER_HOST, SERVER_PORT
from logger import logger


class APIClient:
    def __init__(self, base_url: str = f"http://{SERVER_HOST}:{SERVER_PORT}"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self.client.aclose()

    def set_token(self, token: str) -> None:
        self.token = token

    async def register(self, username: str, email: str, password: str, avatar: str) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "avatar": avatar
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                return data
            else:
                logger.error(f"Registration error: {response.text}")
                error_data = response.json()
                return {"success": False, "detail": error_data.get("detail", "Registration failed")}
        except Exception as e:
            logger.error(f"Registration request error: {str(e)}")
            return None

    async def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                return data
            else:
                logger.error(f"Login error: {response.text}")
                error_data = response.json()
                return {"success": False, "detail": error_data.get("detail", "Login failed")}
        except Exception as e:
            logger.error(f"Login request error: {str(e)}")
            return None

    async def logout(self) -> bool:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/logout",
                params={"token": self.token}
            )
            if response.status_code == 200:
                self.token = None
                return True
            return False
        except Exception as e:
            logger.error(f"Logout request error: {str(e)}")
            return False

    async def search_users(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        try:
            response = await self.client.get(
                f"{self.base_url}/api/users/search",
                params={"query": query, "token": self.token, "limit": limit}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("users", [])
            return None
        except Exception as e:
            logger.error(f"Search users request error: {str(e)}")
            return None

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = await self.client.get(
                f"{self.base_url}/api/users/{user_id}",
                params={"token": self.token}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Get user request error: {str(e)}")
            return None

    async def get_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        try:
            response = await self.client.get(
                f"{self.base_url}/api/messages/{user_id}",
                params={"token": self.token, "limit": limit, "offset": offset}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("messages", [])
            return None
        except Exception as e:
            logger.error(f"Get messages request error: {str(e)}")
            return None

    async def get_chats(self) -> Optional[List[Dict[str, Any]]]:
        try:
            response = await self.client.get(
                f"{self.base_url}/api/chats",
                params={"token": self.token}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("chats", [])
            return None
        except Exception as e:
            logger.error(f"Get chats request error: {str(e)}")
            return None
