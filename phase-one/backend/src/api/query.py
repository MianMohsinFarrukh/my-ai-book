"""
Query API endpoints for RAG functionality
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..services.rag_service import get_rag_service
from ..utils.logging import validation_error, internal_error


router = APIRouter()


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    selected_text: Optional[str] = None
    validate_grounding: bool = True
    include_context: bool = True
    filters: Optional[Dict[str, Any]] = None


class ContextItem(BaseModel):
    source: str
    content: str
    similarity: float
    metadata: Dict[str, Any]


class QueryResponse(BaseModel):
    query: str
    response: str
    context_used: List[ContextItem]
    grounding_confidence: float
    timestamp: str
    sources: List[str]


class ContentSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None


class ContentSearchResponse(BaseModel):
    query: str
    results: List[ContextItem]
    total_results: int


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query endpoint for RAG functionality
    """
    try:
        rag_service = get_rag_service()

        # If selected text is provided, use it as primary context
        if request.selected_text:
            result = await rag_service.query_with_selected_text(
                query=request.query,
                selected_text=request.selected_text,
                top_k=request.top_k,
                validate_grounding=request.validate_grounding
            )
        else:
            # Use regular RAG query
            result = await rag_service.query(
                query=request.query,
                top_k=request.top_k,
                validate_grounding=request.validate_grounding,
                filters=request.filters
            )

        response_text = result.get("response", "")
        context_used = result.get("context_used", [])
        grounding_confidence = result.get("grounding_confidence", 0.0)

        # Format context items for response
        formatted_context = [
            ContextItem(
                source=item.get("metadata", {}).get("source_file", "unknown"),
                content=item.get("content", "")[:500] + "..." if len(item.get("content", "")) > 500 else item.get("content", ""),
                similarity=item.get("similarity", 0.0),
                metadata=item.get("metadata", {})
            )
            for item in context_used
        ]

        # Extract unique sources
        sources = list(set(item.source for item in formatted_context))

        return QueryResponse(
            query=request.query,
            response=response_text,
            context_used=formatted_context,
            grounding_confidence=grounding_confidence,
            timestamp=datetime.utcnow().isoformat(),
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error processing query request: {str(e)}")


@router.post("/search", response_model=ContentSearchResponse)
async def search_endpoint(request: ContentSearchRequest):
    """
    Search endpoint to find relevant content without generating a response
    """
    try:
        rag_service = get_rag_service()

        # Perform semantic search
        search_results = await rag_service.search_content(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )

        # Format results
        formatted_results = [
            ContextItem(
                source=item.get("metadata", {}).get("source_file", "unknown"),
                content=item.get("content", "")[:500] + "..." if len(item.get("content", "")) > 500 else item.get("content", ""),
                similarity=item.get("similarity", 0.0),
                metadata=item.get("metadata", {})
            )
            for item in search_results
        ]

        return ContentSearchResponse(
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )

    except HTTPException:
        raise
    except Exception as e:
        internal_error(f"Error processing search request: {str(e)}")


@router.get("/sources", response_model=List[str])
async def get_sources():
    """
    Get list of all content sources that have been ingested
    """
    try:
        rag_service = get_rag_service()

        sources = await rag_service.get_all_sources()
        return sources

    except Exception as e:
        internal_error(f"Error retrieving sources: {str(e)}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """
    Get statistics about the RAG system
    """
    try:
        rag_service = get_rag_service()

        stats = await rag_service.get_stats()
        return stats

    except Exception as e:
        internal_error(f"Error retrieving stats: {str(e)}")