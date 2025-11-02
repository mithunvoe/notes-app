# 📚 Documentation Index

Welcome to the PDF Notes API documentation! This guide will help you navigate through all available documentation.

## 🚀 Getting Started

1. **[README.md](README.md)** - Start here!
   - Project overview
   - Features and architecture
   - Quick start guide
   - API endpoints
   - Configuration options

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick commands and tips
   - Essential commands
   - API quick reference
   - Common troubleshooting
   - Python client examples

3. **[setup.sh](setup.sh)** - Automated setup script
   - Run this first: `./setup.sh`

## 📖 Core Documentation

### For Users

- **[NOTE_STYLES_GUIDE.md](NOTE_STYLES_GUIDE.md)** - ⭐ NEW! Choose your note style
  - Short, Moderate, or Descriptive
  - Examples and comparisons
  - When to use each style
  - Custom prompt combinations

- **[API_GUIDE.md](API_GUIDE.md)** - Comprehensive API usage guide
  - Detailed endpoint examples
  - cURL and Python examples
  - Batch processing
  - Custom prompts
  - Client library implementation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference card
  - Common commands
  - Environment variables
  - Troubleshooting tips

### For Developers

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
  - What's implemented
  - How everything works
  - Workflow details
  - Key features
  - Next steps

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - High-level architecture diagrams
  - Data flow diagrams
  - Component diagrams
  - Technology stack
  - Deployment options

### For DevOps

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide
  - Local development setup
  - Production deployment options
  - Docker Compose deployment
  - Kubernetes deployment
  - Cloud platform deployment (AWS, GCP, Heroku)
  - Monitoring and logging
  - Backup and recovery
  - Security best practices
  - Scaling strategies

## 🗂️ Technical Documentation

### Database

- **[supabase_schema.sql](supabase_schema.sql)** - Database schema
  - Complete SQL schema
  - Table definitions
  - Indexes
  - Relationships
  - Row-level security policies

### Configuration

- **[.env.example](.env.example)** - Environment variables template
  - All configurable settings
  - Required vs optional variables
  - Default values

- **[config.py](config.py)** - Configuration management
  - Settings class
  - Environment variable loading

### Docker

- **[Dockerfile](Dockerfile)** - Container definition
  - Base image
  - Dependencies
  - Application setup

- **[docker-compose.yml](docker-compose.yml)** - Multi-container orchestration
  - Service definitions
  - Volumes
  - Networks
  - Health checks

## 🧪 Testing

- **[quick_test.py](quick_test.py)** - Quick API test
  - Health check
  - Basic endpoint testing
  - Run after starting services

- **[test_api.py](test_api.py)** - Full integration tests
  - Comprehensive test suite
  - Complete workflow testing
  - Requires pytest

## 📝 Code Documentation

### Main Application

- **[main.py](main.py)** - FastAPI application
  - API endpoints
  - Request/response models
  - Error handling

### Background Tasks

- **[celery_app.py](celery_app.py)** - Celery configuration
  - Broker setup
  - Task configuration
  - Retry policies

- **[tasks.py](tasks.py)** - Celery task definitions
  - `process_file_task` - PDF processing
  - `summarize_chunks_task` - Chunk summarization
  - `synthesize_notes_task` - Note synthesis

### Data Services

- **[database.py](database.py)** - Supabase client
  - Database operations
  - CRUD functions
  - File/chunk/summary/note operations

- **[chroma_client.py](chroma_client.py)** - Vector database client
  - Embedding storage
  - Semantic search
  - Chunk management

- **[llm_service.py](llm_service.py)** - LLM integration
  - Gemini integration
  - OpenAI integration
  - Summarization
  - Synthesis
  - Q&A

### Utilities

- **[utils/text_extraction.py](utils/text_extraction.py)** - PDF text extraction
  - PyMuPDF integration
  - pdfplumber integration
  - Text cleaning
  - Metadata extraction

- **[utils/chunking.py](utils/chunking.py)** - Text chunking
  - Sentence-aware chunking
  - Token counting
  - Overlap management

- **[utils/embeddings.py](utils/embeddings.py)** - Embedding generation
  - Sentence-transformers integration
  - Batch processing
  - Similarity computation

- **[utils/file_utils.py](utils/file_utils.py)** - File utilities
  - SHA256 hashing
  - Directory management

## 📊 Diagrams & Visuals

All diagrams are in **[ARCHITECTURE.md](ARCHITECTURE.md)**:
- High-level architecture
- Data flow diagrams
- Component diagrams
- Technology stack
- Deployment options

## 🔍 Quick Navigation

### I want to...

**...get started quickly**
→ [README.md](README.md) → [setup.sh](setup.sh) → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**...understand the API**
→ [API_GUIDE.md](API_GUIDE.md) → http://localhost:8000/docs

**...deploy to production**
→ [DEPLOYMENT.md](DEPLOYMENT.md)

**...understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md) → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**...set up the database**
→ [supabase_schema.sql](supabase_schema.sql)

**...customize the app**
→ [.env.example](.env.example) → [config.py](config.py)

**...run tests**
→ [quick_test.py](quick_test.py) → [test_api.py](test_api.py)

**...troubleshoot issues**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (Troubleshooting section)

## 📚 External Resources

### Supabase
- Documentation: https://supabase.com/docs
- Create account: https://supabase.com

### Google Gemini
- Documentation: https://ai.google.dev/docs
- Get API key: https://makersuite.google.com/app/apikey

### OpenAI
- Documentation: https://platform.openai.com/docs
- Get API key: https://platform.openai.com/api-keys

### Docker
- Documentation: https://docs.docker.com
- Install: https://docs.docker.com/get-docker/

### Python Libraries
- FastAPI: https://fastapi.tiangolo.com
- Celery: https://docs.celeryproject.org
- Chroma: https://docs.trychroma.com
- Sentence-Transformers: https://www.sbert.net

## 📞 Getting Help

1. Check **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** for common issues
2. Review **[README.md](README.md)** for setup instructions
3. Check API docs at http://localhost:8000/docs
4. Review logs: `docker-compose logs -f`
5. Test health: `python quick_test.py`

## 📋 File Overview

```
Documentation Files (Read these):
├── README.md                 ⭐ Start here
├── NOTE_STYLES_GUIDE.md      ✨ NEW! Choose your note style
├── QUICK_REFERENCE.md        ⭐ Quick commands
├── API_GUIDE.md              📖 API usage
├── DEPLOYMENT.md             🚀 Deployment
├── PROJECT_SUMMARY.md        📊 Overview
├── ARCHITECTURE.md           🏗️  Architecture
└── INDEX.md                  📚 This file

Configuration Files (Edit these):
├── .env.example              🔧 Environment template
├── docker-compose.yml        🐳 Docker setup
├── requirements.txt          📦 Dependencies
└── supabase_schema.sql       🗄️  Database schema

Setup & Testing Files (Run these):
├── setup.sh                  ⚙️  Automated setup
├── quick_test.py             ✅ Quick test
└── test_api.py               🧪 Full tests

Application Code (Understand these):
├── main.py                   🌐 API server
├── celery_app.py             ⚡ Task queue
├── tasks.py                  📋 Background tasks
├── database.py               💾 Database client
├── chroma_client.py          🔍 Vector DB
├── llm_service.py            🤖 AI integration
├── config.py                 ⚙️  Settings
└── utils/                    🛠️  Utilities
    ├── text_extraction.py
    ├── chunking.py
    ├── embeddings.py
    └── file_utils.py
```

## 🎯 Next Steps

1. ✅ Read [README.md](README.md)
2. ✅ Run `./setup.sh`
3. ✅ Edit `.env` with your credentials
4. ✅ Run database schema in Supabase
5. ✅ Start services: `docker-compose up`
6. ✅ Test: `python quick_test.py`
7. ✅ Try the API: http://localhost:8000/docs
8. ✅ Read [API_GUIDE.md](API_GUIDE.md) for usage examples
9. ✅ Deploy with [DEPLOYMENT.md](DEPLOYMENT.md)

## 📝 Notes

- All documentation is in Markdown format
- All code is documented with comments
- All endpoints have OpenAPI documentation
- All configuration is via environment variables
- All services are containerized with Docker

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**License**: MIT
