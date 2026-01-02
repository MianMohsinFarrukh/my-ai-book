"""
Qdrant vector database client setup
"""
import logging
from typing import List, Dict, Optional, Any
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from pydantic_settings import BaseSettings


logger = logging.getLogger(__name__)


class VectorDBSettings(BaseSettings):
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "book_content"
    vector_size: int = 1536
    distance: str = "Cosine"

    class Config:
        env_file = ".env"
        env_prefix = "QDRANT_"
        extra = "ignore"


class VectorDBClient:
    """
    Qdrant client wrapper for vector database operations
    """

    def __init__(self, settings: VectorDBSettings = None):
        self.settings = settings or VectorDBSettings()

        if self.settings.qdrant_url:
            self.client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                prefer_grpc=True
            )
        else:
            self.client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port
            )

        self.collection_name = self.settings.collection_name

    async def init_collection(self) -> None:
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.settings.vector_size,
                        distance=Distance[self.settings.distance.upper()]
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise

    async def add_embeddings(
        self,
        texts: List[str],
        embeddings: List[List[float]],  # New parameter for actual embeddings
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:

        if ids is None:
            ids = [str(uuid4()) for _ in texts]

        # Verify that embeddings list has the same length as texts
        if len(embeddings) != len(texts):
            raise ValueError(f"Number of embeddings ({len(embeddings)}) must match number of texts ({len(texts)})")

        points = [
            PointStruct(
                id=ids[i],
                vector=embeddings[i],  # Use the actual embeddings
                payload={
                    "content": texts[i],
                    **metadata[i]
                }
            )
            for i in range(len(texts))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return ids

    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:

        qdrant_filters = None
        if filters:
            conditions = [
                models.FieldCondition(
                    key=f"metadata.{k}",
                    match=models.MatchValue(value=v)
                )
                for k, v in filters.items()
            ]
            qdrant_filters = models.Filter(must=conditions)

        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                query_filter=qdrant_filters,
                with_payload=True,
                with_vectors=False
            )

            return [
                {
                    "id": r.id,
                    "content": r.payload.get("content", ""),
                    "metadata": r.payload,
                    "similarity": getattr(r, 'score', getattr(r, 'scores', 0.0))
                }
                for r in results.points
            ]
        except Exception as e:
            logger.error(f"Error during Qdrant query: {e}")
            # Return empty results if there's a connection error
            return []

    async def delete_by_source(self, source_file: str) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.source_file",
                                match=models.MatchValue(value=source_file)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted vectors for source: {source_file}")
            return True
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False

    async def get_collection_info(self) -> Dict[str, Any]:
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance,
                "point_count": info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    async def health_check(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Vector database health check failed: {e}")
            return False


# Global instance
_vector_db_client: Optional[VectorDBClient] = None


def get_vector_db_client() -> VectorDBClient:
    global _vector_db_client
    if _vector_db_client is None:
        _vector_db_client = VectorDBClient()
    return _vector_db_client


async def init_vector_db() -> None:
    global _vector_db_client
    try:
        if _vector_db_client is None:
            _vector_db_client = VectorDBClient()

        await _vector_db_client.init_collection()
        logger.info("Vector database initialized successfully")

    except Exception as e:
        logger.warning(
            "Vector database initialization failed "
            "(this is OK for development without Qdrant): %s", e
        )
        logger.warning(
            "The application will run but with limited RAG capabilities"
        )
