"""
Chat message model
"""
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class ChatMessage(Base, TimestampMixin):
    """
    Represents individual messages within a conversation
    """
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', or 'system'
    content = Column(Text, nullable=False)  # The actual message content
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    context_used = Column(JSON, nullable=True)  # JSONB for tracking which content was used
    message_type = Column(String, default="query")  # 'query', 'response', or 'context-only'

    # Relationship to chat session
    session = relationship("ChatSession", back_populates="messages")

    def __init__(self, **kwargs):
        # Validate role
        if 'role' in kwargs and kwargs['role'] not in ['user', 'assistant', 'system']:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")

        # Validate message_type
        if 'message_type' in kwargs and kwargs['message_type'] not in ['query', 'response', 'context-only']:
            raise ValueError("message_type must be 'query', 'response', or 'context-only'")

        super().__init__(**kwargs)


