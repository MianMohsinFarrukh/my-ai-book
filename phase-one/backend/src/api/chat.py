"""
Chat API endpoints
"""
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
import json
from pydantic import BaseModel

from ..models import ChatSession, ChatMessage
from ..database import get_db_session
from ..services.rag_service import get_rag_service
from ..services.ingestion_service import get_ingestion_service
from ..utils.logging import validation_error, internal_error
from ..agents.agent_integration import get_agent_chat_service


router = APIRouter()


# Request/Response models
class ChatRequest(BaseModel):
    query: str
    selected_text: Optional[str] = None
    session_id: Optional[str] = None
    context_override: bool = False
    options: Optional[Dict[str, Any]] = None


class ContextItem(BaseModel):
    source: str
    content: str
    similarity: float


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    context_used: List[ContextItem]
    grounding_confidence: float
    timestamp: str


class IngestionRequest(BaseModel):
    source_path: str
    chunk_size: int = 1000
    overlap: int = 200
    metadata: Optional[Dict[str, Any]] = None


class IngestionResponse(BaseModel):
    status: str
    files_processed: int
    chunks_created: int
    details: Dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for asking questions about book content
    """
    try:
        # Get agent chat service
        agent_service = get_agent_chat_service()

        # Process the chat message using the agent
        result = await agent_service.process_chat_message(
            query=request.query,
            session_id=request.session_id,
            selected_text=request.selected_text
        )

        response_text = result["response"]

        # Extract context and grounding info from agent response if available
        # For now, we'll use a simplified approach
        context_used = []
        grounding_confidence = 0.0

        # If the agent response includes context info, extract it
        if "context_used" in result:
            context_used = result["context_used"]
        if "grounding_confidence" in result:
            grounding_confidence = result.get("grounding_confidence", 0.0)

        # Create or get chat session
        provided_session_id = result.get("session_id", request.session_id)
        session_created = False  # Track if we created a new session

        # Save the interaction to database
        async with get_db_session() as db_session:
            from sqlalchemy import select
            import uuid
            session = None

            # If a session_id was provided by the client, try to find the existing session
            if provided_session_id:
                try:
                    existing_session_uuid = uuid.UUID(provided_session_id)
                    existing_session = await db_session.execute(
                        select(ChatSession).where(ChatSession.id == existing_session_uuid)
                    )
                    session = existing_session.scalar()
                except ValueError:
                    # If the provided session_id is not a valid UUID, we'll create a new session
                    pass

            # If no session was found or no session_id was provided, create a new one
            if not session:
                new_session_uuid = uuid.uuid4()
                session = ChatSession(
                    id=new_session_uuid,
                    user_id=None  # Could be set based on authentication
                )
                db_session.add(session)
                session_created = True

            await db_session.commit()

            # Create user message
            user_message = ChatMessage(
                session_id=session.id,  # session.id is already a UUID object
                role="user",
                content=request.query,
                context_used=context_used,
                message_type="query"
            )
            db_session.add(user_message)

            # Create assistant message
            assistant_message = ChatMessage(
                session_id=session.id,  # session.id is already a UUID object
                role="assistant",
                content=response_text,
                context_used=context_used,
                message_type="response"
            )
            db_session.add(assistant_message)

            await db_session.commit()

        # Format context items for response
        formatted_context = [
            ContextItem(
                source=item.get("metadata", {}).get("source_file", "unknown") if isinstance(item, dict) else "unknown",
                content=item.get("content", "")[:500] + "..." if len(item.get("content", "")) > 500 else item.get("content", "") if isinstance(item, dict) else item[:500] + "..." if len(str(item)) > 500 else str(item),
                similarity=item.get("similarity", 0.0) if isinstance(item, dict) else 0.0
            )
            for item in context_used
        ]

        return ChatResponse(
            response=response_text,
            session_id=str(session.id),
            message_id=str(uuid4()),  # Generate a new message ID
            context_used=formatted_context,
            grounding_confidence=grounding_confidence,
            timestamp=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error processing chat request: {str(e)}")


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_endpoint(request: IngestionRequest):
    """
    Endpoint for ingesting book content
    """
    try:
        ingestion_service = get_ingestion_service()

        # Validate request
        if not request.source_path:
            validation_error("Source path is required")

        # Perform ingestion
        results = await ingestion_service.ingest_directory(request.source_path)

        # Calculate statistics
        files_processed = len(results)
        chunks_created = sum(len(ids) for ids in results.values())

        return IngestionResponse(
            status="success",
            files_processed=files_processed,
            chunks_created=chunks_created,
            details=results
        )

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error during ingestion: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """
    Get a specific chat session
    """
    try:
        async with get_db_session() as db_session:
            from sqlalchemy import select
            import uuid
            # Convert string session_id to UUID for comparison with UUID column
            try:
                session_uuid = uuid.UUID(session_id)
            except ValueError:
                validation_error(f"Invalid session ID format: {session_id}")

            result = await db_session.execute(
                select(ChatSession).where(ChatSession.id == session_uuid)
            )
            session = result.scalar()

            if not session:
                validation_error(f"Session with ID {session_id} not found")

            return {
                "session_id": str(session.id),
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "is_active": session.is_active
            }

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error retrieving session: {str(e)}")


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """
    Get all messages for a specific session
    """
    try:
        async with get_db_session() as db_session:
            from sqlalchemy import select
            import uuid
            # Convert string session_id to UUID for comparison with UUID column
            try:
                session_uuid = uuid.UUID(session_id)
            except ValueError:
                validation_error(f"Invalid session ID format: {session_id}")

            result = await db_session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_uuid)
                .order_by(ChatMessage.timestamp)
            )
            messages = result.scalars().all()

            return [
                {
                    "message_id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "context_used": msg.context_used
                }
                for msg in messages
            ]

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error retrieving session messages: {str(e)}")


async def stream_chat_response(query: str, selected_text: Optional[str] = None, context_override: bool = False):
    """
    Generator function that streams chat responses
    """
    try:
        # Get agent chat service
        agent_service = get_agent_chat_service()

        # Process the chat message using the agent
        result = await agent_service.process_chat_message(
            query=query,
            session_id=None,  # For streaming, we create a new session
            selected_text=selected_text
        )

        response_text = result["response"]

        # Extract context and grounding info from agent response if available
        context_used = result.get("context_used", [])
        grounding_confidence = result.get("grounding_confidence", 0.0)

        # Create a new chat session for streaming
        session_created = False

        # Save the interaction to database
        async with get_db_session() as db_session:
            import uuid
            session = None

            # For streaming, always create a new session
            new_session_uuid = uuid.uuid4()
            session = ChatSession(
                id=new_session_uuid,
                user_id=None  # Could be set based on authentication
            )
            db_session.add(session)
            session_created = True

            # Create user message
            user_message = ChatMessage(
                session_id=session.id,  # session.id is already a UUID object
                role="user",
                content=query,
                context_used=context_used,
                message_type="query"
            )
            db_session.add(user_message)

            # Create assistant message
            assistant_message = ChatMessage(
                session_id=session.id,  # session.id is already a UUID object
                role="assistant",
                content=response_text,
                context_used=context_used,
                message_type="response"
            )
            db_session.add(assistant_message)

            await db_session.commit()

        # Stream the response in chunks
        chunk_size = 10  # Number of characters per chunk
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

        # Send context/sources at the end
        formatted_context = [
            {
                "source": item.get("metadata", {}).get("source_file", "unknown") if isinstance(item, dict) else "unknown",
                "content": item.get("content", "")[:500] + "..." if len(item.get("content", "")) > 500 else item.get("content", "") if isinstance(item, dict) else item[:500] + "..." if len(str(item)) > 500 else str(item),
                "similarity": item.get("similarity", 0.0) if isinstance(item, dict) else 0.0
            }
            for item in context_used
        ]

        yield f"data: {json.dumps({'type': 'sources', 'sources': formatted_context})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post("/chat/stream", response_class=StreamingResponse)
async def stream_chat_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses
    """
    async def generate():
        async for chunk in stream_chat_response(
            query=request.query,
            selected_text=request.selected_text,
            context_override=request.context_override
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")