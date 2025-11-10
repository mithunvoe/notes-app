from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
import os
from uuid import uuid4
from datetime import datetime

from config import settings
from database import db
from tasks import process_file_task
from chroma_client import chroma_service
# Use new Strategy Pattern for LLM
from patterns.strategy import LLMContext
from utils import compute_bytes_hash, ensure_directory, embedding_service

# Initialize LLM context with strategy pattern
llm_context = LLMContext()  # Auto-selects strategy based on config


# Create FastAPI app
app = FastAPI(
    title="PDF Notes API",
    description="AI-powered PDF note-taking backend with RAG capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
ensure_directory(settings.upload_dir)


# Enum for note styles
class NoteStyle(str, Enum):
    """
    Note style options:
    - short: Brief bullet points, only key facts
    - moderate: Balanced notes with main points and some details
    - descriptive: Comprehensive notes with full explanations
    """
    short = "short"
    moderate = "moderate"
    descriptive = "descriptive"


# Pydantic models
class UploadResponse(BaseModel):
    file_id: str
    task_id: str
    filename: str
    status: str
    message: str


class FileStatus(BaseModel):
    file_id: str
    filename: str
    status: str
    created_at: str
    updated_at: str
    error: Optional[str] = None


class NoteResponse(BaseModel):
    file_id: str
    note_text: str
    metadata: Optional[dict] = None
    created_at: str


class QuestionRequest(BaseModel):
    question: str
    n_results: int = 5


class AnswerResponse(BaseModel):
    answer: str
    sources: List[dict]
    model_info: dict


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PDF Notes API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "status": "/status/{file_id}",
            "note": "/notes/{file_id}",
            "qa": "/qa/{file_id}",
            "files": "/files"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Chroma
        chunk_count = chroma_service.count()
        
        return {
            "status": "healthy",
            "chroma": {
                "connected": True,
                "total_chunks": chunk_count
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    note_style: NoteStyle = Form(NoteStyle.moderate),
    user_prompt: Optional[str] = Form(None)
):
    """
    Upload a PDF file for processing.
    
    Args:
        file: PDF file to upload
        note_style: Style of notes to generate:
            - short: Quick bullet points with only the most important facts
            - moderate: Balanced notes with main ideas and key details (default)
            - descriptive: Detailed comprehensive notes with full explanations
        user_prompt: Optional custom instructions for note generation
    
    Returns:
        Upload response with file_id and task_id
    
    Example:
        Upload with moderate style (default):
        curl -X POST "http://localhost:8000/upload" \\
          -F "file=@document.pdf" \\
          -F "note_style=moderate"
        
        Upload with short style and custom prompt:
        curl -X POST "http://localhost:8000/upload" \\
          -F "file=@document.pdf" \\
          -F "note_style=short" \\
          -F "user_prompt=Focus on methodology only"
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Check file size
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.max_file_size} bytes"
            )
        
        # Compute file hash
        file_hash = compute_bytes_hash(content)
        
        # Check if file already exists
        existing_file = db.get_file_by_hash(file_hash)
        if existing_file:
            return UploadResponse(
                file_id=existing_file['id'],
                task_id="",
                filename=existing_file['original_filename'],
                status=existing_file['status'],
                message="File already exists (duplicate detected)"
            )
        
        # Generate unique file ID and save file
        file_id = str(uuid4())
        filename = f"{file_id}.pdf"
        file_path = os.path.join(settings.upload_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create file record in database
        file_data = {
            'id': file_id,
            'filename': filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'sha256': file_hash,
            'file_size': len(content),
            'status': 'uploaded',
            'user_prompt': user_prompt
        }
        db.create_file(file_data)
        
        # Enqueue processing task with note style
        task = process_file_task.delay(file_id, file_path, note_style.value, user_prompt)
        
        return UploadResponse(
            file_id=file_id,
            task_id=task.id,
            filename=file.filename,
            status='uploaded',
            message="File uploaded successfully and queued for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/status/{file_id}", response_model=FileStatus)
async def get_file_status(file_id: str):
    """
    Get processing status of a file.
    
    Args:
        file_id: File ID
    
    Returns:
        File status information
    """
    file_info = db.get_file(file_id)
    
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileStatus(
        file_id=file_info['id'],
        filename=file_info['original_filename'],
        status=file_info['status'],
        created_at=file_info['created_at'],
        updated_at=file_info['updated_at'],
        error=file_info.get('error')
    )


@app.get("/files")
async def list_files(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all uploaded files with pagination.
    
    Args:
        limit: Number of files to return (1-100, default 10)
        offset: Offset for pagination (default 0)
    
    Returns:
        Paginated list of files with metadata
    
    Example:
        curl -X GET "http://localhost:8001/files?limit=20&offset=0"
    """
    try:
        result = db.list_files(limit=limit, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )


@app.get("/notes/{file_id}", response_model=NoteResponse)
async def get_note(file_id: str):
    """
    Get the generated note for a file.
    
    Args:
        file_id: File ID
    
    Returns:
        Generated note
    """
    # Check if file exists
    file_info = db.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check status
    if file_info['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Note not ready. Current status: {file_info['status']}"
        )
    
    # Get note
    note = db.get_note_by_file(file_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(
        file_id=file_id,
        note_text=note['note_text'],
        metadata=note.get('metadata'),
        created_at=note['created_at']
    )


@app.post("/qa/{file_id}", response_model=AnswerResponse)
async def ask_question(file_id: str, request: QuestionRequest):
    """
    Ask a question about a specific file using RAG.
    
    Args:
        file_id: File ID to query
        request: Question request with query text
    
    Returns:
        Answer with sources
    """
    # Check if file exists and is processed
    file_info = db.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_info['status'] not in ['indexed', 'summarizing', 'completed']:
        raise HTTPException(
            status_code=400,
            detail=f"File not ready for queries. Status: {file_info['status']}"
        )
    
    try:
        # Embed the question
        question_embedding = embedding_service.embed_text(request.question)
        
        # Query Chroma for relevant chunks
        results = chroma_service.query(
            query_embeddings=[question_embedding],
            n_results=request.n_results,
            where={"file_id": file_id},
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'][0]:
            raise HTTPException(
                status_code=404,
                detail="No relevant content found"
            )
        
        # Get retrieved documents and metadata
        retrieved_docs = results['documents'][0]
        retrieved_meta = results['metadatas'][0]
        distances = results['distances'][0]
        
        # Prepare sources with relevance scores
        sources = []
        for i, (meta, distance) in enumerate(zip(retrieved_meta, distances)):
            sources.append({
                'chunk_index': meta['chunk_index'],
                'relevance_score': float(1 - distance),  # Convert distance to similarity
                'preview': retrieved_docs[i][:200] + "..." if len(retrieved_docs[i]) > 200 else retrieved_docs[i]
            })
        
        # Generate answer using LLM (Strategy Pattern)
        answer_result = llm_context.answer_question(
            request.question,
            retrieved_docs
        )
        
        return AnswerResponse(
            answer=answer_result['text'],
            sources=sources,
            model_info={
                'provider': answer_result['provider'],
                'model': answer_result['model'],
                'tokens_used': answer_result.get('tokens_used', 0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )


@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file and all associated data.
    
    Args:
        file_id: File ID to delete
    
    Returns:
        Deletion confirmation
    """
    # Check if file exists
    file_info = db.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Delete from Chroma
        chroma_service.delete_by_file_id(file_id)
        
        # Delete physical file
        if os.path.exists(file_info['file_path']):
            os.remove(file_info['file_path'])
        
        # Database CASCADE will delete chunks, summaries, and notes
        # This depends on your database client implementation
        
        return {
            "message": "File deleted successfully",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deletion failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
