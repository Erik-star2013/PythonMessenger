from database import Database, User
from security import hash_password, verify_password, create_access_token
from models import UserLoginRequest, UserRegisterRequest, UserResponse
from typing import Optional, Tuple
from logger import logger


class AuthManager:
    def __init__(self, db: Database):
        self.db = db

    def register_user(self, request: UserRegisterRequest) -> Tuple[bool, str, Optional[UserResponse]]:
        try:
            session = self.db.get_session()
            
            existing_user = self.db.get_user_by_username(session, request.username)
            if existing_user:
                return False, "Username already taken", None

            existing_email = self.db.get_user_by_email(session, request.email)
            if existing_email:
                return False, "Email already registered", None

            password_hash = hash_password(request.password)
            user = self.db.create_user(session, request.username, request.email, password_hash, request.avatar)
            
            session.close()
            logger.info(f"User registered: {request.username}")
            
            user_response = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                avatar=user.avatar,
                is_online=user.is_online
            )
            return True, "Registration successful", user_response
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}", None

    def login_user(self, request: UserLoginRequest) -> Tuple[bool, str, Optional[dict]]:
        try:
            session = self.db.get_session()
            
            user = self.db.get_user_by_username(session, request.username)
            if not user or not verify_password(request.password, user.password_hash):
                session.close()
                return False, "Invalid username or password", None

            token = create_access_token({"sub": user.username, "user_id": user.id})
            self.db.set_user_online(session, user.id, True)
            
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "avatar": user.avatar,
                "token": token
            }
            
            session.close()
            logger.info(f"User logged in: {request.username}")
            
            return True, "Login successful", user_data
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}", None

    def logout_user(self, user_id: int) -> bool:
        try:
            session = self.db.get_session()
            self.db.set_user_online(session, user_id, False)
            session.close()
            logger.info(f"User logged out: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False
