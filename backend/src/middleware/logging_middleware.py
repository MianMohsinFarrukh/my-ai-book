"""
Logging middleware for the RAG Chatbot API
"""
import time
import uuid
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """
    Middleware to log requests and responses
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        request_id = str(uuid.uuid4())

        # Get start time
        start_time = time.time()

        # Log the incoming request
        logger.info(
            f"REQUEST {request_id} - {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(dict(request.query_params)),
                "client": request.client.host if request.client else None
            }
        )

        # Capture response
        response_body = b""

        async def send_with_capture(message):
            if message["type"] == "http.response.body":
                nonlocal response_body
                response_body += message.get("body", b"")

            # Add request ID to response headers
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers

            await send(message)

        # Process the request
        try:
            await self.app(scope, receive, send_with_capture)
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time

            logger.error(
                f"REQUEST {request_id} - ERROR: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": duration,
                    "error": str(e)
                }
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log the response
        logger.info(
            f"RESPONSE {request_id} - Status: 200",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration": duration,
                "response_size": len(response_body)
            }
        )


def setup_logging_middleware(app):
    """
    Setup logging middleware for the application
    """
    app.add_middleware(LoggingMiddleware)
    return app