"""FastAPI routes for the RAG assistant."""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from ..core.config import settings
from ..core.logger import logger
from .dependencies import (
    get_rag_pipeline,
    get_vector_store,
    get_cache_manager,
    get_memory_manager,
)

router = APIRouter()


# Request/Response Models
class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    top_k: Optional[int] = 5
    use_hybrid: Optional[bool] = True
    use_reranker: Optional[bool] = False
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: List[Dict[str, Any]]
    session_id: str
    cached: bool = False


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    filename: str
    num_chunks: int
    status: str
    message: str


class CollectionStats(BaseModel):
    """Collection statistics."""
    total_documents: int
    collection_name: str
    status: str


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Nepal RAG Assistant"}


# Query endpoint
@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system.
    
    Args:
        request: Query request with question and parameters
        
    Returns:
        Answer with sources and session ID
    """
    try:
        logger.info(f"Received query: {request.query[:100]}")
        
        # Get components
        rag = get_rag_pipeline()
        cache = get_cache_manager()
        memory = get_memory_manager()
        
        # Check cache first
        cached_response = await cache.get_cached_response(request.query)
        if cached_response:
            logger.info("Returning cached response")
            return QueryResponse(
                answer=cached_response["answer"],
                sources=cached_response["sources"],
                session_id=request.session_id or "default",
                cached=True,
            )
        
        # Get conversation history if session provided
        history = []
        if request.session_id:
            history = await memory.get_history(request.session_id)
        
        # Process query
        result = await rag.query(
            query=request.query,
            top_k=request.top_k,
            use_hybrid=request.use_hybrid,
            use_reranker=request.use_reranker,
            history=history,
        )
        
        # Cache the response
        await cache.cache_response(request.query, result)
        
        # Save to conversation memory
        session_id = request.session_id or "default"
        await memory.add_interaction(
            session_id=session_id,
            query=request.query,
            response=result["answer"],
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=session_id,
            cached=False,
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Upload PDF endpoint
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload and process a PDF document.
    
    Args:
        file: PDF file to upload
        background_tasks: FastAPI background tasks
        
    Returns:
        Upload status and document info
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check file size
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
            )
        
        # Save file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved file: {file_path}")
        
        # Process document
        rag = get_rag_pipeline()
        num_chunks = await rag.ingest_document(str(file_path))
        
        return DocumentUploadResponse(
            filename=file.filename,
            num_chunks=num_chunks,
            status="success",
            message=f"Document processed successfully. Added {num_chunks} chunks.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get collection stats
@router.get("/stats", response_model=CollectionStats)
async def get_collection_stats():
    """Get vector store statistics."""
    try:
        vector_store = get_vector_store()
        count = vector_store.count_documents()
        
        return CollectionStats(
            total_documents=count,
            collection_name=settings.qdrant_collection_name,
            status="active",
        )
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# List uploaded documents
@router.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    try:
        upload_dir = Path(settings.upload_dir)
        if not upload_dir.exists():
            return {"documents": []}
        
        documents = []
        for pdf_file in upload_dir.glob("*.pdf"):
            documents.append({
                "filename": pdf_file.name,
                "size_mb": round(pdf_file.stat().st_size / (1024 * 1024), 2),
                "uploaded_at": pdf_file.stat().st_mtime,
            })
        
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Clear cache
@router.post("/cache/clear")
async def clear_cache():
    """Clear the response cache."""
    try:
        cache = get_cache_manager()
        await cache.clear_cache()
        return {"status": "success", "message": "Cache cleared"}
        
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get conversation history
@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session."""
    try:
        memory = get_memory_manager()
        history = await memory.get_history(session_id)
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Clear conversation history
@router.delete("/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """Clear conversation history for a session."""
    try:
        memory = get_memory_manager()
        await memory.clear_history(session_id)
        return {"status": "success", "message": f"History cleared for {session_id}"}
        
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
