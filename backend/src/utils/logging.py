"""
Logging and error handling infrastructure
"""
import logging
import sys
from typing import Dict, Any
from datetime import datetime
from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppLogger:
    """
    Application logger with structured logging
    """
    def __init__(self, name: str = "book-rag-chatbot", level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # Create console handler with formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logger.debug(message, extra=extra)

    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(message, extra=extra)

    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logger.warning(message, extra=extra)

    def error(self, message: str, extra: Dict[str, Any] = None):
        self.logger.error(message, extra=extra)

    def critical(self, message: str, extra: Dict[str, Any] = None):
        self.logger.critical(message, extra=extra)

    def log_structured(self, level: LogLevel, message: str, **kwargs):
        """
        Log structured data with additional context
        """
        structured_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "message": message,
            **kwargs
        }
        getattr(self.logger, level.lower())(f"Structured log: {structured_data}")


# Global logger instance
app_logger = AppLogger()


class APIError(BaseModel):
    """
    Standardized API error response model
    """
    error: str
    message: str
    timestamp: str = datetime.utcnow().isoformat()
    path: str = ""
    details: Dict[str, Any] = {}


class CustomHTTPException(HTTPException):
    """
    Custom HTTP exception with structured error response
    """
    def __init__(self, status_code: int, error: str, message: str, details: Dict[str, Any] = None):
        super().__init__(
            status_code=status_code,
            detail=APIError(
                error=error,
                message=message,
                details=details or {}
            ).model_dump()
        )


def handle_error(status_code: int, error: str, message: str, details: Dict[str, Any] = None):
    """
    Helper function to raise standardized API errors
    """
    raise CustomHTTPException(
        status_code=status_code,
        error=error,
        message=message,
        details=details or {}
    )


# Common error handlers
def not_found_error(entity: str, identifier: str = None):
    """
    Raise a 404 Not Found error
    """
    message = f"{entity} not found"
    if identifier:
        message += f" with identifier: {identifier}"

    handle_error(
        status_code=status.HTTP_404_NOT_FOUND,
        error="NOT_FOUND",
        message=message
    )


def validation_error(message: str, details: Dict[str, Any] = None):
    """
    Raise a 422 Validation Error
    """
    handle_error(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error="VALIDATION_ERROR",
        message=message,
        details=details or {}
    )


def internal_error(message: str = "An internal error occurred"):
    """
    Raise a 500 Internal Server Error
    """
    handle_error(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error="INTERNAL_ERROR",
        message=message
    )


def bad_request_error(message: str, details: Dict[str, Any] = None):
    """
    Raise a 400 Bad Request error
    """
    handle_error(
        status_code=status.HTTP_400_BAD_REQUEST,
        error="BAD_REQUEST",
        message=message,
        details=details or {}
    )