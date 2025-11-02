# PDF Notes API - AI-Powered Note-Taking Backend

An intelligent note-taking backend that processes PDF documents, generates structured notes using AI, and provides RAG (Retrieval-Augmented Generation) capabilities for Q&A.

## Features

- 📄 **PDF Processing**: Automatic text extraction from PDF files
- 🔍 **Smart Chunking**: Sentence-aware text chunking with overlap
- 📝 **Three Note Styles**: Choose between Short, Moderate, or Descriptive notes
- 🧠 **AI Summarization**: Per-chunk and hierarchical note synthesis using Gemini/OpenAI
- 🔎 **RAG Q&A**: Answer questions about your documents with source attribution
- ⚡ **Async Processing**: Background task processing with Celery
- 🗄️ **Vector Search**: Fast semantic search using Chroma vector database
- 💾 **Supabase Integration**: Reliable metadata storage
- 🔄 **Deduplication**: Automatic file deduplication using SHA256 hashing
- 🎯 **Custom Prompts**: Add your own instructions for personalized notes

## Architecture

```
┌─────────────┐
│   FastAPI   │  (API Endpoints)
└──────┬──────┘
       │
       ├─────► Upload PDF → Redis Queue
       │
       ├─────► Get Status
       │
       └─────► Query (RAG)
              
┌──────────────┐
│Celery Workers│ (Background Tasks)
└──────┬───────┘
       │
       ├─────► Extract Text (PyMuPDF)
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

## Tech Stack

- **API Framework**: FastAPI
- **Task Queue**: Celery + Redis
- **Vector DB**: Chroma (with DuckDB+Parquet backend)
- **Database**: Supabase (PostgreSQL)
- **PDF Processing**: PyMuPDF, pdfplumber
- **Embeddings**: sentence-transformers
- **LLM**: Google Gemini / OpenAI (configurable)
- **Deployment**: Docker + Docker Compose

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Supabase account (free tier works)
- Gemini API key (free) or OpenAI API key

### 2. Setup Supabase

1. Create a new project on [Supabase](https://supabase.com)
2. Run the SQL schema from `supabase_schema.sql` in the SQL editor
3. Get your project URL and keys from Settings > API
  - For the backend server, prefer the Service Role key (server-only, never expose to browsers)

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
# Use the service role key on the server to avoid RLS errors
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
# (Alternatively for quick local dev you can keep the anon key as SUPABASE_KEY,
#  but RLS policies will block inserts unless you adjust them.)
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

Services will be available at:
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Flower (Task Monitor)**: http://localhost:5555

### 5. Test the API

#### Upload a PDF

**Simple upload (uses default Moderate style):**
```bash
curl -X POST "http://localhost:8001/upload" \
  -F "file=@your-document.pdf"
```

**With note style selection:**
```bash
# Short notes - Quick bullet points
curl -X POST "http://localhost:8001/upload" \
  -F "file=@your-document.pdf" \
  -F "note_style=short"

# Moderate notes - Balanced (default)
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your-document.pdf" \
  -F "note_style=moderate"

# Descriptive notes - Detailed and comprehensive
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your-document.pdf" \
  -F "note_style=descriptive"
```

**With custom prompt:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your-document.pdf" \
  -F "note_style=moderate" \
  -F "user_prompt=Focus on key concepts and examples"
```

Response:
```json
{
  "file_id": "abc-123-def",
  "task_id": "task-456",
  "filename": "your-document.pdf",
  "status": "uploaded",
  "message": "File uploaded successfully and queued for processing"
}
```

#### Check Processing Status

```bash
curl "http://localhost:8000/status/abc-123-def"
```

Status progression: `uploaded` → `processing` → `indexed` → `summarizing` → `completed`

#### Get Generated Notes

```bash
curl "http://localhost:8000/notes/abc-123-def"
```

#### Ask Questions (RAG)

```bash
curl -X POST "http://localhost:8000/qa/abc-123-def" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics discussed?",
    "n_results": 5
  }'
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/upload` | Upload PDF file (with note style & custom prompt) |
| GET | `/status/{file_id}` | Get processing status |
| GET | `/notes/{file_id}` | Get generated notes |
| POST | `/qa/{file_id}` | Ask questions (RAG) |
| DELETE | `/files/{file_id}` | Delete file and data |

### Note Styles

When uploading, you can choose from three note styles:

- **short**: Quick bullet points with only key facts
- **moderate**: Balanced notes with main ideas and details (default)
- **descriptive**: Comprehensive notes with full explanations

See [NOTE_STYLES_GUIDE.md](NOTE_STYLES_GUIDE.md) for detailed examples and usage.

Full API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | Required |
| `SUPABASE_KEY` | Supabase anon key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `LLM_PROVIDER` | LLM provider (`gemini`, `openai`, `local`) | `gemini` |
| `CHUNK_SIZE` | Target chunk size in tokens | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks in tokens | `200` |
| `EMBEDDING_MODEL` | Sentence-transformers model | `all-MiniLM-L6-v2` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |

### Chunking Strategy

The system uses intelligent chunking:
- **Sentence-aware**: Never splits mid-sentence
- **Token-based**: Uses tiktoken for accurate token counting
- **Overlap**: Maintains context between chunks
- **Adaptive**: Handles long sentences by word-splitting

### LLM Configuration

#### Using Gemini (Free Tier)

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-pro
```

Gemini free tier includes:
- 60 queries per minute
- 1,500 queries per day
- 1M tokens per day

#### Using OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-3.5-turbo
```

## Development

### Running Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Start Redis
redis-server

# Start Celery worker
celery -A celery_app.celery worker --loglevel=info

# Start FastAPI
uvicorn main:app --reload
```

### Project Structure

```
notes/
├── main.py                 # FastAPI application
├── celery_app.py          # Celery configuration
├── tasks.py               # Celery tasks
├── config.py              # Settings
├── database.py            # Supabase client
├── chroma_client.py       # Chroma vector DB client
├── llm_service.py         # LLM integration
├── utils/
│   ├── text_extraction.py # PDF text extraction
│   ├── chunking.py        # Text chunking logic
│   ├── embeddings.py      # Embedding computation
│   └── file_utils.py      # File utilities
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Multi-container setup
├── supabase_schema.sql   # Database schema
└── .env.example          # Environment template
```

## Workflow Details

### 1. Upload & Processing

```
User uploads PDF
    ↓
FastAPI saves file & creates DB record
    ↓
Enqueues process_file_task
    ↓
Worker extracts text (PyMuPDF)
    ↓
Chunks text (sentence-aware, 1000 tokens)
    ↓
Computes embeddings (sentence-transformers)
    ↓
Stores in Chroma + Supabase
    ↓
Status: indexed
```

### 2. Summarization

```
Enqueues summarize_chunks_task
    ↓
For each chunk:
  - Calls LLM (Gemini/OpenAI)
  - Stores summary in DB
    ↓
All chunks summarized
    ↓
Status: summarizing
```

### 3. Note Synthesis

```
Enqueues synthesize_notes_task
    ↓
Gets all chunk summaries
    ↓
If many summaries (>20):
  - Hierarchical synthesis (groups of 10)
Else:
  - Direct synthesis
    ↓
Stores final note in DB
    ↓
Status: completed
```

### 4. RAG Q&A

```
User asks question
    ↓
Embed question (sentence-transformers)
    ↓
Query Chroma (top-k similar chunks)
    ↓
Assemble prompt with retrieved chunks
    ↓
Call LLM for answer
    ↓
Return answer + sources with relevance scores
```

## Monitoring

### Celery Task Monitoring (Flower)

Access Flower at http://localhost:5555 to:
- Monitor active tasks
- View task history
- Check worker status
- Inspect task results

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f worker

# View API logs
docker-compose logs -f app
```

## Production Considerations

### Security

1. **API Authentication**: Add JWT or API key authentication
2. **CORS**: Configure allowed origins in production
3. **File Validation**: Add virus scanning
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Secrets**: Use proper secret management (not .env files)

### Scalability

1. **Horizontal Scaling**: Add more Celery workers
2. **Task Prioritization**: Use Celery task priorities
3. **Caching**: Add Redis caching for frequent queries
4. **CDN**: Serve static content via CDN
5. **Load Balancing**: Use nginx or similar for load balancing

### Persistence

1. **Backups**: Regular backups of Supabase and Chroma data
2. **Volume Mounts**: Ensure persistent volumes for uploads and Chroma
3. **Database Indexing**: Add indexes for frequent queries

### Cost Optimization

1. **LLM Usage**: 
   - Use Gemini free tier for development
   - Cache LLM responses
   - Batch API calls where possible
2. **Storage**: Clean up old files regularly
3. **Compute**: Auto-scale workers based on queue length

## Troubleshooting

### Common Issues

**Import errors when running**
```bash
# Install dependencies
pip install -r requirements.txt
```

**Celery tasks not processing**
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

**Chroma persistence issues**
```bash
# Ensure volume is mounted
docker-compose down
docker volume ls
docker-compose up
```

**Out of memory**
```bash
# Reduce worker concurrency in docker-compose.yml
command: celery -A celery_app.celery worker --concurrency=1
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: [See /docs endpoint]
