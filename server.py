from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Optional
from datetime import timedelta
from datetime import datetime

from config import SERVER_HOST, SERVER_PORT, ACCESS_TOKEN_EXPIRE_MINUTES
from database import db, init_db
from auth import AuthManager
from models import UserLoginRequest, UserRegisterRequest, SearchUserRequest
from websocket_server import WebSocketManager
from security import decode_access_token, create_access_token
from logger import logger

app = FastAPI(title="PythonMessenger", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_manager = AuthManager(db)
ws_manager = WebSocketManager(db)


@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Server started")


@app.on_event("shutdown")
async def shutdown_event():
    db.close()
    logger.info("Server shutdown")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}


@app.post("/api/auth/register")
async def register(request: UserRegisterRequest):
    success, message, user = auth_manager.register_user(request)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    token = create_access_token(
        {"sub": user["username"], "user_id": user["id"]},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "success": True,
        "message": message,
        "user": user,
        "token": token
    }


@app.post("/api/auth/login")
async def login(request: UserLoginRequest):
    success, message, user_data = auth_manager.login_user(request)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    
    return {
        "success": True,
        "message": message,
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "avatar": user_data["avatar"],
        "token": user_data["token"]
    }


@app.post("/api/auth/logout")
async def logout(token: str = Query(...)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    success = auth_manager.logout_user(user_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Logout failed")
    
    return {"success": True, "message": "Logged out successfully"}


@app.get("/api/users/search")
async def search_users(query: str = Query(...), token: str = Query(...), limit: int = 10):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("user_id")
    session = db.get_session()
    users = db.search_users(session, query, user_id, limit)
    session.close()
    
    return {
        "success": True,
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "avatar": u.avatar,
                "is_online": u.is_online,
                "last_seen": u.last_seen.isoformat() if u.last_seen else None
            }
            for u in users
        ]
    }


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, token: str = Query(...)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    session = db.get_session()
    user = db.get_user_by_id(session, user_id)
    session.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
        "is_online": user.is_online,
        "last_seen": user.last_seen.isoformat() if user.last_seen else None
    }


@app.get("/api/messages/{user_id}")
async def get_messages(user_id: int, token: str = Query(...), limit: int = 50, offset: int = 0):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    current_user_id = payload.get("user_id")
    session = db.get_session()
    messages = db.get_messages(session, current_user_id, user_id, limit, offset)
    session.close()
    
    return {
        "success": True,
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "recipient_id": m.recipient_id,
                "content": m.content,
                "message_type": m.message_type.value,
                "file_path": m.file_path,
                "status": m.status.value,
                "created_at": m.created_at.isoformat(),
                "edited_at": m.edited_at.isoformat() if m.edited_at else None
            }
            for m in reversed(messages)
        ]
    }


@app.get("/api/chats")
async def get_chats(token: str = Query(...)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    current_user_id = payload.get("user_id")
    session = db.get_session()
    messages = db.get_recent_chats(session, current_user_id)
    
    chats = {}
    for msg in messages:
        other_user_id = msg.recipient_id if msg.sender_id == current_user_id else msg.sender_id
        if other_user_id not in chats:
            other_user = db.get_user_by_id(session, other_user_id)
            if other_user:
                chats[other_user_id] = {
                    "user_id": other_user_id,
                    "username": other_user.username,
                    "avatar": other_user.avatar,
                    "is_online": other_user.is_online,
                    "last_message": msg.content,
                    "last_message_time": msg.created_at.isoformat()
                }
    
    session.close()
    
    return {
        "success": True,
        "chats": list(chats.values())
    }


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = payload.get("user_id")
    await websocket.accept()
    
    try:
        await ws_manager.connect(websocket, user_id)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            
            if action == "message":
                recipient_id = message.get("recipient_id")
                content = message.get("content")
                await ws_manager.send_message(user_id, recipient_id, content)
            
            elif action == "typing":
                recipient_id = message.get("recipient_id")
                is_typing = message.get("is_typing")
                await ws_manager.broadcast_typing(user_id, recipient_id, is_typing)
            
            elif action == "read_receipt":
                message_id = message.get("message_id")
                await ws_manager.send_read_receipt(message_id, user_id)
            
            elif action == "edit_message":
                message_id = message.get("message_id")
                new_content = message.get("new_content")
                await ws_manager.edit_message(message_id, new_content, user_id)
            
            elif action == "delete_message":
                message_id = message.get("message_id")
                await ws_manager.delete_message(message_id, user_id)
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await ws_manager.disconnect(user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
