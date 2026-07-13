from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from typing import Optional, List
from config import DATABASE_URL, DATABASE_PATH
from models import MessageStatus, MessageType
import os

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    avatar = Column(String, default="😀")
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    file_path = Column(String, nullable=True)
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.SENT)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")


class Database:
    def __init__(self):
        if os.path.exists(DATABASE_PATH):
            self.engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
            Base.metadata.create_all(bind=self.engine)

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_tables(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def create_user(self, session: Session, username: str, email: str, password_hash: str, avatar: str) -> User:
        db_user = User(username=username, email=email, password_hash=password_hash, avatar=avatar)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    def get_user_by_username(self, session: Session, username: str) -> Optional[User]:
        return session.query(User).filter(User.username == username).first()

    def get_user_by_id(self, session: Session, user_id: int) -> Optional[User]:
        return session.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, session: Session, email: str) -> Optional[User]:
        return session.query(User).filter(User.email == email).first()

    def search_users(self, session: Session, query: str, exclude_user_id: int, limit: int = 10) -> List[User]:
        return session.query(User).filter(
            User.username.ilike(f"%{query}%"),
            User.id != exclude_user_id
        ).limit(limit).all()

    def set_user_online(self, session: Session, user_id: int, is_online: bool) -> None:
        user = self.get_user_by_id(session, user_id)
        if user:
            user.is_online = is_online
            if not is_online:
                user.last_seen = datetime.utcnow()
            session.commit()

    def create_message(
        self,
        session: Session,
        sender_id: int,
        recipient_id: int,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        file_path: Optional[str] = None
    ) -> Message:
        db_message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            file_path=file_path,
            status=MessageStatus.SENT
        )
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return db_message

    def get_messages(
        self,
        session: Session,
        user_id_1: int,
        user_id_2: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        return session.query(Message).filter(
            (
                (Message.sender_id == user_id_1) & (Message.recipient_id == user_id_2) |
                (Message.sender_id == user_id_2) & (Message.recipient_id == user_id_1)
            ),
            Message.is_deleted == False
        ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

    def get_recent_chats(self, session: Session, user_id: int, limit: int = 20) -> List[Message]:
        return session.query(Message).filter(
            (Message.sender_id == user_id) | (Message.recipient_id == user_id),
            Message.is_deleted == False
        ).order_by(Message.created_at.desc()).limit(limit * 2).all()

    def get_message_by_id(self, session: Session, message_id: int) -> Optional[Message]:
        return session.query(Message).filter(Message.id == message_id).first()

    def update_message_status(self, session: Session, message_id: int, status: MessageStatus) -> None:
        message = self.get_message_by_id(session, message_id)
        if message:
            message.status = status
            session.commit()

    def edit_message(self, session: Session, message_id: int, new_content: str) -> None:
        message = self.get_message_by_id(session, message_id)
        if message:
            message.content = new_content
            message.edited_at = datetime.utcnow()
            session.commit()

    def delete_message(self, session: Session, message_id: int) -> None:
        message = self.get_message_by_id(session, message_id)
        if message:
            message.is_deleted = True
            session.commit()

    def count_unread_messages(self, session: Session, recipient_id: int, sender_id: int) -> int:
        return session.query(Message).filter(
            Message.recipient_id == recipient_id,
            Message.sender_id == sender_id,
            Message.status != MessageStatus.READ,
            Message.is_deleted == False
        ).count()

    def search_messages(self, session: Session, user_id_1: int, user_id_2: int, query: str) -> List[Message]:
        return session.query(Message).filter(
            (
                (Message.sender_id == user_id_1) & (Message.recipient_id == user_id_2) |
                (Message.sender_id == user_id_2) & (Message.recipient_id == user_id_1)
            ),
            Message.content.ilike(f"%{query}%"),
            Message.is_deleted == False
        ).order_by(Message.created_at.desc()).all()


db = Database()
