"""
Chat session model
"""
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """
    Represents a user's conversation with the chatbot
    """
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, nullable=True)  # Optional user identifier
    metadata_ = Column("metadata", JSON, nullable=True)  # JSONB column for session metadata
    is_active = Column(Boolean, default=True)  # Whether the session is currently active
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to chat messages
    messages = relationship("ChatMessage", order_by="ChatMessage.timestamp", back_populates="session", cascade="all, delete-orphan")