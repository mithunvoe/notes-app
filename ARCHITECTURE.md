# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT / USER                            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                       FASTAPI (main.py)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │ /upload  │ /status  │ /notes   │   /qa    │   /health    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
└──────┬──────────────────────┬──────────────────────────┬───────┘
       │                      │                          │
       │ Enqueue Task         │ Query DB                 │ Query Vector DB
       │                      │                          │
┌──────▼─────┐      ┌─────────▼──────────┐    ┌─────────▼──────────┐
│   REDIS    │      │     SUPABASE       │    │      CHROMA        │
│  (Broker)  │      │   (PostgreSQL)     │    │   (Vector DB)      │
│            │      │                    │    │                    │
│  - Queue   │      │  - files           │    │  - Embeddings      │
│  - Results │      │  - chunks          │    │  - Documents       │
└──────┬─────┘      │  - summaries       │    │  - Metadata        │
       │            │  - notes           │    │  - Semantic Search │
       │            └────────────────────┘    └────────────────────┘
       │
       │ Pull Tasks
       │
┌──────▼──────────────────────────────────────────────────────────┐
│                    CELERY WORKERS                                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              process_file_task                             │ │
│  │  1. Extract text (PyMuPDF)                                 │ │
│  │  2. Chunk text (sentence-aware)                            │ │
│  │  3. Generate embeddings (sentence-transformers)            │ │
│  │  4. Store in Chroma + Supabase                             │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │            summarize_chunks_task                           │ │
│  │  1. Fetch chunks from DB                                   │ │
│  │  2. Call LLM for each chunk (Gemini/OpenAI)               │ │
│  │  3. Store summaries in DB                                  │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │           synthesize_notes_task                            │ │
│  │  1. Fetch all summaries                                    │ │
│  │  2. Hierarchical synthesis if many                         │ │
│  │  3. Call LLM for final note                                │ │
│  │  4. Store final note in DB                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ API Calls
                           │
                 ┌─────────▼─────────┐
                 │   LLM SERVICES    │
                 │  ┌─────────────┐  │
                 │  │   Gemini    │  │
                 │  │  (Google)   │  │
                 │  └─────────────┘  │
                 │  ┌─────────────┐  │
                 │  │   OpenAI    │  │
                 │  │   (GPT)     │  │
                 │  └─────────────┘  │
                 └───────────────────┘
```

## Data Flow Diagram

### Upload & Processing Flow

```
┌──────┐
│ USER │
└───┬──┘
    │
    │ 1. Upload PDF
    │
┌───▼────────┐
│  FastAPI   │
└───┬────────┘
    │
    │ 2. Save file + Create DB record
    │
┌───▼────────┐     ┌──────────┐
│  Supabase  │◄────┤ file.pdf │
│   files    │     │  (disk)  │
└────────────┘     └──────────┘
    │
    │ 3. Enqueue task
    │
┌───▼────────┐
│   Redis    │
│   Queue    │
└───┬────────┘
    │
    │ 4. Worker pulls task
    │
┌───▼────────────────┐
│  Celery Worker     │
│                    │
│  Extract Text      │
│       ↓            │
│  Chunk Text        │
│       ↓            │
│  Generate          │
│  Embeddings        │
└───┬────────────────┘
    │
    │ 5. Store chunks + embeddings
    │
┌───▼────────┐     ┌──────────┐
│  Supabase  │     │  Chroma  │
│   chunks   │     │  vectors │
└────────────┘     └──────────┘
```

### Summarization Flow

```
┌──────────────┐
│ Celery Worker│
└───┬──────────┘
    │
    │ 1. Fetch chunks
    │
┌───▼────────┐
│  Supabase  │
│   chunks   │
└───┬────────┘
    │
    │ 2. For each chunk
    │
┌───▼────────────┐
│  LLM Service   │
│  (Gemini/GPT)  │
└───┬────────────┘
    │
    │ 3. Store summaries
    │
┌───▼────────┐
│  Supabase  │
│ summaries  │
└────────────┘
```

### Synthesis Flow

```
┌──────────────┐
│ Celery Worker│
└───┬──────────┘
    │
    │ 1. Fetch all summaries
    │
┌───▼────────┐
│  Supabase  │
│ summaries  │
└───┬────────┘
    │
    │ 2. Group summaries (if many)
    │
┌───▼────────────┐
│  LLM Service   │
│  Synthesize    │
│  (Hierarchical)│
└───┬────────────┘
    │
    │ 3. Store final note
    │
┌───▼────────┐
│  Supabase  │
│   notes    │
└────────────┘
```

### RAG Query Flow

```
┌──────┐
│ USER │
└───┬──┘
    │
    │ 1. Ask question
    │
┌───▼────────┐
│  FastAPI   │
└───┬────────┘
    │
    │ 2. Embed question
    │
┌───▼────────────┐
│  Embeddings    │
│  Service       │
└───┬────────────┘
    │
    │ 3. Semantic search
    │
┌───▼────────┐
│  Chroma    │
│  Query     │
└───┬────────┘
    │
    │ 4. Top-k chunks
    │
┌───▼────────────┐
│  LLM Service   │
│  RAG Answer    │
└───┬────────────┘
    │
    │ 5. Answer + Sources
    │
┌───▼────────┐
│  FastAPI   │
│  Response  │
└────────────┘
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                          │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐  │
│  │    app     │  │   worker   │  │   redis    │  │  flower  │  │
│  │            │  │            │  │            │  │          │  │
│  │  FastAPI   │  │   Celery   │  │   Queue    │  │ Monitor  │  │
│  │  :8000     │  │  Workers   │  │   :6379    │  │  :5555   │  │
│  └─────┬──────┘  └──────┬─────┘  └─────┬──────┘  └──────────┘  │
│        │                │              │                         │
│        └────────────────┴──────────────┘                         │
│                         │                                        │
│                         │ Shared Volumes                         │
│                         │                                        │
│        ┌────────────────┴──────────────────┐                    │
│        │                                   │                    │
│  ┌─────▼──────┐                  ┌─────────▼────┐              │
│  │  uploads/  │                  │ data/chroma/ │              │
│  │  (PDFs)    │                  │  (Vectors)   │              │
│  └────────────┘                  └──────────────┘              │
└──────────────────────────────────────────────────────────────────┘
         │                                   │
         │                                   │
         │ External Services                 │
         │                                   │
┌────────▼──────────┐              ┌─────────▼─────────┐
│    Supabase       │              │   LLM APIs        │
│  (PostgreSQL)     │              │                   │
│                   │              │  - Google Gemini  │
│  - files          │              │  - OpenAI GPT     │
│  - chunks         │              │                   │
│  - summaries      │              └───────────────────┘
│  - notes          │
└───────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FastAPI    │  │    Celery    │  │   Pydantic   │          │
│  │   (API)      │  │   (Tasks)    │  │  (Validation)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Layer                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   PyMuPDF    │  │  Tiktoken    │  │  Sentence-   │          │
│  │  (PDF Read)  │  │  (Tokens)    │  │ Transformers │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │    NLTK      │  │  pdfplumber  │                            │
│  │ (Sentences)  │  │  (Tables)    │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                       Storage Layer                              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Supabase    │  │   Chroma     │  │    Redis     │          │
│  │ (PostgreSQL) │  │  (Vectors)   │  │   (Queue)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Layer                                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │    Gemini    │  │   OpenAI     │                            │
│  │  (Free/Paid) │  │   (Paid)     │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Options

```
┌──────────────────────────────────────────────────────────────┐
│                   Local Development                           │
│                                                              │
│  Docker Compose                                              │
│    ↓                                                         │
│  All services on one machine                                 │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                 Production - Single Server                    │
│                                                              │
│  Docker Compose + Nginx + SSL                                │
│    ↓                                                         │
│  VPS (DigitalOcean, AWS EC2, etc.)                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              Production - Kubernetes                          │
│                                                              │
│  K8s Deployment                                              │
│    ↓                                                         │
│  Auto-scaling, Load balancing                                │
│    ↓                                                         │
│  GKE, EKS, AKS                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│             Production - Serverless                           │
│                                                              │
│  Cloud Run / Lambda                                          │
│    ↓                                                         │
│  Pay per use, auto-scaling                                   │
│    ↓                                                         │
│  Google Cloud Run, AWS Lambda                                │
└──────────────────────────────────────────────────────────────┘
```
