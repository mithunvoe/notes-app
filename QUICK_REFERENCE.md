# Quick Reference Card

## Essential Commands

### Setup & Start
```bash
./setup.sh              # Initial setup
docker-compose up       # Start all services
docker-compose up -d    # Start in background
docker-compose down     # Stop all services
```

### Testing
```bash
python quick_test.py    # Quick health check
python test_api.py      # Full integration tests
```

### Monitoring
```bash
docker-compose logs -f          # All logs
docker-compose logs -f worker   # Worker logs
docker-compose logs -f app      # API logs
```

### URLs
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Flower: http://localhost:5555

## API Quick Reference

### Upload PDF

**Simple upload (default moderate style):**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

**With note style:**
```bash
# Short - Quick bullet points
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf" \
  -F "note_style=short"

# Moderate - Balanced (default)
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf" \
  -F "note_style=moderate"

# Descriptive - Detailed
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf" \
  -F "note_style=descriptive"
```

**With custom prompt:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf" \
  -F "note_style=moderate" \
  -F "user_prompt=Focus on methodology only"
```

### Check Status
```bash
curl http://localhost:8000/status/{file_id}
```

### Get Notes
```bash
curl http://localhost:8000/notes/{file_id}
```

### Ask Question
```bash
curl -X POST http://localhost:8000/qa/{file_id} \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?", "n_results": 5}'
```

### Delete File
```bash
curl -X DELETE http://localhost:8000/files/{file_id}
```

## Environment Variables

Required:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GEMINI_API_KEY=your-api-key  # or OPENAI_API_KEY
```

Optional:
```env
LLM_PROVIDER=gemini          # gemini, openai, local
CHUNK_SIZE=1000              # tokens
CHUNK_OVERLAP=200            # tokens
MAX_FILE_SIZE=52428800       # 50MB in bytes
```

## Status Values

- `uploaded` → File saved, queued
- `processing` → Extracting & chunking
- `indexed` → Stored in vector DB
- `summarizing` → Generating summaries
- `completed` → Ready to use
- `failed` → Check error field

## File Structure

```
main.py              # API endpoints
tasks.py             # Celery tasks
database.py          # Supabase client
chroma_client.py     # Vector DB
llm_service.py       # AI integration
utils/               # Utilities
  ├── text_extraction.py
  ├── chunking.py
  └── embeddings.py
```

## Docker Commands

```bash
# Build
docker-compose build

# Start/Stop
docker-compose up -d
docker-compose down

# Restart service
docker-compose restart worker

# View logs
docker-compose logs -f

# Execute command
docker-compose exec app bash
docker-compose exec redis redis-cli

# Clean up
docker-compose down -v  # Remove volumes too
```

## Troubleshooting

### Workers not processing
```bash
docker-compose restart worker
docker-compose logs worker
```

### Can't connect to API
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Chroma issues
```bash
docker-compose down
docker volume ls
docker-compose up -d
```

### Out of memory
```bash
docker stats
# Reduce concurrency in docker-compose.yml
```

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Upload with note style
response = requests.post(
    f"{BASE_URL}/upload",
    files={'file': open('doc.pdf', 'rb')},
    data={
        'note_style': 'moderate',  # short, moderate, or descriptive
        'user_prompt': 'Focus on main findings'  # optional
    }
)
file_id = response.json()['file_id']

# Wait for completion
import time
while True:
    status = requests.get(f"{BASE_URL}/status/{file_id}").json()
    if status['status'] == 'completed':
        break
    time.sleep(5)

# Get notes
notes = requests.get(f"{BASE_URL}/notes/{file_id}").json()
print(notes['note_text'])

# Ask question
answer = requests.post(
    f"{BASE_URL}/qa/{file_id}",
    json={'question': 'Summarize the main points'}
).json()
print(answer['answer'])
```

## Database Tables

- `files` - Uploaded file metadata
- `chunks` - Text chunks from PDFs
- `summaries` - Per-chunk summaries
- `notes` - Final synthesized notes

All use UUID primary keys and have proper foreign key relationships.

## Processing Flow

```
Upload → Extract → Chunk → Embed → Store → Summarize → Synthesize
  ↓        ↓        ↓       ↓       ↓         ↓          ↓
uploaded processing indexed indexed summarizing completed
```

## Common Customizations

### Choose note style
```bash
# In API request
-F "note_style=short"      # Quick bullets
-F "note_style=moderate"   # Balanced (default)
-F "note_style=descriptive" # Detailed
```
See [NOTE_STYLES_GUIDE.md](NOTE_STYLES_GUIDE.md) for examples

### Change chunk size
```env
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```

### Use different LLM
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4
```

### Increase worker concurrency
```yaml
# docker-compose.yml
worker:
  command: celery -A celery_app.celery worker --concurrency=4
```

### Change embedding model
```env
EMBEDDING_MODEL=all-mpnet-base-v2  # More accurate but slower
```

## Production Checklist

- [ ] Set environment to production
- [ ] Configure proper secrets
- [ ] Set up SSL/HTTPS
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Configure auto-scaling
- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Set up CI/CD
- [ ] Configure logging
- [ ] Test disaster recovery

## Support Files

- `README.md` - Full documentation
- `API_GUIDE.md` - API usage examples
- `DEPLOYMENT.md` - Deployment guide
- `PROJECT_SUMMARY.md` - Complete overview
- `supabase_schema.sql` - Database schema

## Tips

1. Always check `/health` endpoint first
2. Monitor tasks at http://localhost:5555
3. Use `user_prompt` for better summaries
4. Keep chunks at 1000-1500 tokens for best results
5. Use Gemini for free tier, OpenAI for quality
6. Back up Chroma data regularly
7. Clean up old files periodically
8. Monitor API rate limits

## Quick Debugging

```bash
# Check all services
docker-compose ps

# Check Redis
docker-compose exec redis redis-cli ping

# Check Chroma
curl http://localhost:8000/health

# Check Celery
curl http://localhost:5555

# Restart everything
docker-compose restart
```
