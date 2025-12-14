"""Qdrant vector store client for document storage and retrieval."""

from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from qdrant_client.http import models
import uuid

from ..core.config import settings
from ..core.logger import logger


class QdrantStore:
    """Qdrant vector database client."""

    def __init__(self, embedding_dimension: int = 384):
        """
        Initialize Qdrant client.
        
        Args:
            embedding_dimension: Dimension of embedding vectors
        """
        self.collection_name = settings.qdrant_collection_name
        self.embedding_dimension = embedding_dimension
        
        # Initialize client based on configuration
        if settings.qdrant_use_cloud and settings.qdrant_url:
            logger.info(f"Connecting to Qdrant Cloud: {settings.qdrant_url}")
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
        else:
            logger.info(f"Connecting to local Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
            )
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def add_documents(self, 
                     texts: List[str], 
                     embeddings: List[List[float]], 
                     metadatas: Optional[List[Dict]] = None) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
            
        Returns:
            List of document IDs
        """
        if len(texts) != len(embeddings):
            raise ValueError("Number of texts and embeddings must match")
        
        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Number of metadatas must match texts")
        
        logger.info(f"Adding {len(texts)} documents to Qdrant")
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Prepare points
        points = []
        for i, (text, embedding, doc_id) in enumerate(zip(texts, embeddings, ids)):
            payload = {
                "text": text,
                "metadata": metadatas[i] if metadatas else {},
            }
            
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload=payload,
            )
            points.append(point)
        
        # Upload to Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            logger.info(f"Successfully added {len(points)} documents")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to Qdrant: {e}")
            raise

    def search(self, 
              query_vector: List[float], 
              top_k: int = 5,
              filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of search results with text, metadata, and scores
        """
        logger.debug(f"Searching Qdrant with top_k={top_k}")
        
        try:
            # Build filter if provided
            query_filter = None
            if filter_dict:
                query_filter = self._build_filter(filter_dict)
            
            # Search using query method
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                query_filter=query_filter,
            ).points
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score,
                })
            
            logger.debug(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}")
            raise

    def _build_filter(self, filter_dict: Dict) -> Filter:
        """
        Build Qdrant filter from dictionary.
        
        Args:
            filter_dict: Dictionary of field-value pairs
            
        Returns:
            Qdrant Filter object
        """
        conditions = []
        for key, value in filter_dict.items():
            conditions.append(
                FieldCondition(
                    key=f"metadata.{key}",
                    match=MatchValue(value=value),
                )
            )
        
        return Filter(must=conditions)

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting {len(ids)} documents from Qdrant")
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=ids),
            )
            logger.info("Documents deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False

    def get_collection_info(self) -> Dict:
        """
        Get collection information.
        
        Returns:
            Dictionary with collection stats
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def delete_collection(self) -> bool:
        """
        Delete the entire collection.
        
        Returns:
            True if successful
        """
        try:
            logger.warning(f"Deleting collection: {self.collection_name}")
            self.client.delete_collection(self.collection_name)
            logger.info("Collection deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def count_documents(self) -> int:
        """
        Get total number of documents in collection.
        
        Returns:
            Number of documents
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
