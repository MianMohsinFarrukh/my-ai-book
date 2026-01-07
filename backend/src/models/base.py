"""
Base model for SQLAlchemy models
"""
from typing import TYPE_CHECKING
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import expression


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base class for all SQLAlchemy models
    """
    pass


class TimestampMixin:
    """
    Mixin class to add created_at and updated_at timestamps
    """
    if TYPE_CHECKING:
        # For type checking purposes
        created_at: Mapped[DateTime]
        updated_at: Mapped[DateTime]

    __allow_unmapped__ = True  # Allow unmapped attributes for older-style declarations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())