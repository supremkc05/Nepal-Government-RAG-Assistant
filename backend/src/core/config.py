from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings are loaded from the environment variables."""

    #app
    app_name: str = "Nepal Government Services Chat Assistant"
    app_version: str ="0.1.0"
    environment: str = "development"
    
    # api server
    api_host: str ="0.0.0.0"
    api_port: int =8000
    api_reload: bool = True

    # llm configuration
    llm_provider: str = "gemini"
    gemini_api_key: Optional[str] = None
    google_api_key: Optional[str] = None # alternative name for gemini_api_key
    openai_api_key: Optional[str] = None

    # embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # qdrant vector store
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "nepal_gov_docs"
    qdrant_use_cloud: bool = False
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None

    # redis cache & memory
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    cache_ttl_seconds: int = 86400 # 24 hours

    # text processing
    chunk_size: int = 1000
    chunk_overlap: int = 120

    # retrieval
    top_k_retrieval: int = 5
    use_reranker: bool = False
    cohere_api_key: Optional[str] = None

    # file storage
    upload_dir: str = "./data/uploads"
    processed_dir: str = "./data/processed"
    max_upload_size_mb: int = 50

    # security
    api_key: str = "change-this-secret-key"
    allowed_origins:str ="http://localhost:8501,http://localhost:3000"

    #logging
    log_level: str = "info"
    log_file: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore" #ignore extra variables in the .env file instead of raising an error

settings = Settings()