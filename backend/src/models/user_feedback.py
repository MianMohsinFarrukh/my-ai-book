"""
User feedback model
"""
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base, TimestampMixin


class UserFeedback(Base, TimestampMixin):
    """
    Stores user feedback on chat responses to improve quality over time
    """
    __tablename__ = "user_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=True)  # Optional: feedback on specific message
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=True)  # Optional: feedback on session
    feedback_type = Column(String, nullable=False)  # 'positive', 'negative', or 'incorrect'
    comment = Column(Text, nullable=True)  # Optional user comment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)  # Whether the feedback has been addressed

    def __init__(self, **kwargs):
        # Validate feedback_type
        if 'feedback_type' in kwargs and kwargs['feedback_type'] not in ['positive', 'negative', 'incorrect']:
            raise ValueError("feedback_type must be 'positive', 'negative', or 'incorrect'")

        # Validate that either message_id or session_id is provided
        message_id = kwargs.get('message_id')
        session_id = kwargs.get('session_id')
        if not message_id and not session_id:
            raise ValueError("Either message_id or session_id must be provided")

        super().__init__(**kwargs)