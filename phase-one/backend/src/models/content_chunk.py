"""
Content chunk model
"""
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base, TimestampMixin


class ContentChunk(Base, TimestampMixin):
    """
    Represents processed chunks of book content stored in the relational database
    (metadata only; vectors stored in Qdrant)
    """
    __tablename__ = "content_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_file = Column(String, nullable=False)  # e.g., 'docs/intro.md'
    chunk_index = Column(Integer, nullable=False)  # Index within the source document
    content = Column(Text, nullable=False)  # The actual content chunk
    embedding_id = Column(String, nullable=False, unique=True)  # References Qdrant point ID
    metadata_ = Column("metadata", JSON, nullable=True)  # Additional content metadata
    hash = Column(String, nullable=True)  # For detecting content changes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, **kwargs):
        # Validate chunk_index
        if 'chunk_index' in kwargs and kwargs['chunk_index'] < 0:
            raise ValueError("chunk_index must be non-negative")

        super().__init__(**kwargs)