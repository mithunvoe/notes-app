# Project Workflow Overview

This document explains the end-to-end workflow of the PDF Notes API: from file upload, through processing and summarization, to RAG-style Q&A. It also outlines the main components, data flow, and state transitions.

## Architecture at a Glance

- FastAPI application (`main.py`) exposes HTTP endpoints
- Celery workers (`celery_app.py`, `tasks.py`) run background jobs
- Vector DB via Chroma (`chroma_client.py`) stores embeddings for retrieval
- Supabase (`database.py`) stores metadata, chunks, summaries, and final notes
- LLM providers (`llm_service.py`) generate summaries and synthesized notes
- Utils (`utils/*`) handle extraction, chunking, embeddings, files, and state management

## High-Level Flow

1) Upload PDF
- Client POSTs `/upload` with a PDF and optional note style and prompt
- API validates file, deduplicates by SHA256, stores file to `uploads/`
- Creates file record in Supabase with status `uploaded`
- Enqueues `process_file_task` (Celery)

2) Processing (Background)
- `process_file_task` sets state to `processing`
- Extracts text from PDF (`utils/text_extraction.py`)
- Chunks text with sentence awareness (`utils/chunking.py`)
- Embeds chunks in batches (`utils/embeddings.py`)
- Stores chunks+embeddings in Chroma and chunks in Supabase
- Sets state to `indexed`
- Enqueues `summarize_chunks_task`

3) Summarization (Background)
- `summarize_chunks_task` sets state to `summarizing`
- Iterates all chunks, calls `LLMService.generate_summary(...)` per chunk
- Stores each summary in Supabase (`summaries` table)
- Observes provider rate limits (delays added for Gemini)
- Enqueues `synthesize_notes_task` once summaries exist

4) Synthesis (Background)
- `synthesize_notes_task` reads all summaries for the file
- If many summaries, performs hierarchical synthesis (groups → final)
- Post-processes math-like pseudo-code to TeX-friendly blocks
- Stores final synthesized note in Supabase (`notes` table)
- Optionally writes local Markdown file to `notes/`
- Sets state to `completed`

5) Retrieval (RAG) & Downloads
- `/qa/{file_id}` embeds the question, queries Chroma for top-k chunks
- Builds an answer prompt with retrieved sources, calls the LLM provider
- Returns answer with source previews and model info
- `/notes/{file_id}` returns final note (JSON or an HTML page)
- `/notes/{file_id}/download` returns Markdown; `/download-pdf` returns a styled PDF

## Components and Responsibilities

- FastAPI (`main.py`)
  - Endpoints: upload, status, files list, notes, note downloads, QA, retry, delete
  - Input validation, error handling, and response shape (Pydantic models)

- Celery Tasks (`tasks.py`)
  - `process_file_task`: extract → chunk → embed → index → enqueue summarization
  - `summarize_chunks_task`: per-chunk LLM summary → store in DB → enqueue synthesis
  - `synthesize_notes_task`: combine summaries → store final note → mark completed
  - `CallbackTask.on_failure`: marks failed state if a task crashes

- State Management (`utils/state.py`)
  - `FileProcessingContext` and concrete states (`Uploaded`, `Processing`, `Indexed`, `Summarizing`, `Completed`, `Failed`)
  - Centralizes DB status updates and provides explicit transitions

- Vector Store (`chroma_client.py`)
  - `ChromaService`: add/query/delete chunks, count helpers

- Database Access (`database.py`)
  - `SupabaseClient`: CRUD for `files`, `chunks`, `summaries`, `notes`, list & cleanup utilities

- LLM Provider Abstraction (`llm_service.py`)
  - Strategy-style switch between Gemini and OpenAI implementations
  - Methods for chunk summary, note synthesis, and question answering

- Utilities (`utils/`)
  - `text_extraction.py`: page text extraction (PyMuPDF/pdfplumber), cleaning, metadata
  - `chunking.py`: sentence-aware chunking with overlap and token budgeting
  - `embeddings.py`: sentence-transformers model, batch encode, cosine similarity
  - `file_utils.py`: hashing, filesystem helpers, markdown save, filename generation

## State Transitions

States are persisted in Supabase `files.status` and driven by `FileProcessingContext`:

```
uploaded → processing → indexed → summarizing → completed
                    ↘─────────────── on error ─────────────→ failed
```

- Set to `processing` at the start of `process_file_task`
- Set to `indexed` after embeddings are stored
- Set to `summarizing` when chunk summarization starts
- Set to `completed` after final note is stored
- Any exception transitions to `failed` with an error message

## Data Flow

- Input: PDF bytes → stored on disk in `uploads/` and recorded in `files`
- Extracted text: combined and cleaned string (not stored directly)
- Chunks: stored twice
  - Text + metadata in Supabase `chunks`
  - Embeddings + metadata in Chroma collection `pdf_chunks`
- Summaries: per-chunk in Supabase `summaries`
- Final note: in Supabase `notes` (+ optional local Markdown)

## RAG Query Flow

1) `/qa/{file_id}` receives question
2) Embed question via `EmbeddingService`
3) Query Chroma by `file_id` with top-k results (documents+metadatas)
4) Build prompt with sources; call LLM provider
5) Return answer + source previews + model info

## Error Handling & Resilience

- Task failures captured by `CallbackTask.on_failure` → state `failed`
- Rate limiting handled in `summarize_chunks_task` with provider-aware delays
- Defensive checks (empty text, missing chunks, empty results) raise actionable errors
- `/files/{file_id}/retry` cleans partial data, resets status, and re-enqueues processing
- Delete endpoint purges data from Chroma, Supabase, local files

## Configuration

- Settings in `config.py` (provider selection, model names, batch sizes, directories)
- Important env: Supabase URL/key, Gemini/OpenAI keys, Chroma persist dir

## Performance Considerations

- Batch embeddings with configurable batch size
- Minimal repeated I/O (persist Chroma once per batch)
- Optional local Markdown saves
- Sentence-aware chunking with token-based overlap for better retrieval and summarization

## Extensibility

- New LLM providers can be added behind `LLMService` methods
- Alternate chunking strategies can be introduced in `utils/chunking.py`
- Additional states or transitions can be added to `FileProcessingContext`
- New retrieval logic (filters, reranking) can be added in `chroma_client.py`

## Key Endpoints

- `POST /upload` — enqueue processing of a PDF
- `GET /status/{file_id}` — current status and errors (if any)
- `GET /files` — list uploaded files (paginated)
- `GET /files/{file_id}/chunks` — debug view of chunks
- `GET /notes/{file_id}` — get final note (JSON or HTML layout)
- `GET /notes/{file_id}/download` — download Markdown
- `GET /notes/{file_id}/download-pdf` — download styled PDF
- `POST /qa/{file_id}` — ask a question (RAG)
- `POST /files/{file_id}/retry` — clean and retry a failed/non-complete file
- `DELETE /files/{file_id}` — delete everything for a file

## Sequence Summary

Upload → Process → Index → Summarize → Synthesize → Complete → (Query/Download)

- This pipeline is orchestrated by Celery tasks and guarded by explicit state transitions.
- Results are queryable via RAG and downloadable as Markdown or PDF.

## ASCII Architecture Diagram

```
┌─────────────┐
│   FastAPI   │  (API Endpoints)
└──────┬──────┘
       │
       ├─────► Upload PDF → Redis/Celery Queue
       │
       ├─────► Get Status / Notes / Download / QA
       │
       └─────► Retry / Delete
              
┌──────────────┐
│Celery Workers│ (Background Tasks)
└──────┬───────┘
       │
       ├─────► Extract Text (PyMuPDF/pdfplumber)
       │
       ├─────► Chunk Text (Sentence-aware)
       │
       ├─────► Compute Embeddings (Sentence-Transformers)
       │
       ├─────► Store in Chroma + Supabase
       │
       ├─────► Summarize Chunks (Gemini/OpenAI)
       │
       └─────► Synthesize Notes (Hierarchical)

┌─────────────┐   ┌──────────────┐   ┌─────────┐
│   Chroma    │   │   Supabase   │   │  Redis  │
│ (Embeddings)│   │  (Metadata)  │   │ (Queue) │
└─────────────┘   └──────────────┘   └─────────┘
```

