from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    # Optional: use service role key on the server to bypass RLS safely
    # If provided, this will be preferred over supabase_key
    supabase_service_role_key: Optional[str] = None
    
    # Celery/Redis
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # Chroma
    chroma_persist_dir: str = "/data/chroma"
    
    # LLM
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_provider: str = "gemini"  # gemini, openai, or local
    gemini_model: str = "gemini-2.5-flash"  # Flash model: faster, cheaper, better rate limits
    gemini_max_output_tokens: int = 60000  # Maximum output tokens for Gemini (Gemini 2.0+ supports up to 32,768)
    openai_model: str = "gpt-3.5-turbo"
    
    # Application
    upload_dir: str = "./uploads"
    notes_dir: str = "./notes"  # Directory to save markdown notes locally
    save_notes_locally: bool = os.getenv("SAVE_NOTES_LOCALLY")  # Whether to save notes as .md files locally
    max_file_size: int = 52428800  # 50MB
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Prefer the service role key when available (server-side only)
# This avoids RLS policy blocks when the backend performs inserts/updates.
if getattr(settings, "supabase_service_role_key", None):
    # Overwrite to keep existing codepaths using settings.supabase_key working
    settings.supabase_key = settings.supabase_service_role_key  # type: ignore
