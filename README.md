# Nepal Government RAG Assistant

A production-ready RAG (Retrieval-Augmented Generation) system that helps citizens get instant answers about Nepal government services using official documents.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)

## Features

- **AI-Powered Q&A**: Answer questions about passports, citizenship, driving licenses, taxes, and more
- **Document Processing**: Upload and process PDF, DOC, DOCX, TXT files automatically
- **Hybrid Search**: Combines vector search (Qdrant) and semantic retrieval for accurate answers
- **Smart Caching**: Redis-based caching for lightning-fast responses
- **Conversation Memory**: Maintains context across conversations
- **Source Citations**: Shows exact document sources for every answer
- **Modern React UI**: Professional, responsive interface with real-time updates
- **Docker Ready**: One-command deployment with docker-compose
- **Real-time Stats**: Live statistics and document management
- **Bilingual Support**: English and Nepali language toggle

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React UI  │────▶│   FastAPI    │────▶│   Qdrant    │
│  (Port 3000)│     │  (Port 8000) │     │  VectorDB   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Redis     │
                    │ Cache/Memory │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Google Gemini│
                    │  2.5-flash   │
                    └──────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Google Gemini API key

### 1. Clone Repository

```bash
git clone https://github.com/supremkc05/Nepal-Government-RAG-Assistant.git
cd Nepal-Government-RAG-Assistant
```

### 2. Configure Environment

Create `.env` file in the root directory:

```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Qdrant Cloud (if not using local Docker)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key

# Vector Store Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=nepal_gov_docs

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
CACHE_TTL_SECONDS=86400

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 4. Access Your Application

- **React Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Backend API**: http://localhost:8000

## Usage Guide

### 1. Upload Documents

Click the upload area in the left sidebar to add government documents:
- Supported formats: PDF, DOC, DOCX, TXT
- Documents are automatically processed and indexed
- View all uploaded documents in the sidebar list

### 2. Ask Questions

Type your question in the chat interface:
- "How do I apply for a passport?"
- "What are citizenship requirements?"
- "How to register a business in Nepal?"

### 3. View Statistics

Monitor your system in the left sidebar:
- Total documents processed
- System status
- Collection information

### 4. Quick Actions

Use pre-configured buttons for common queries:
- Passport Information
- Citizenship
- Tax Filing
- Driving License
- Business Registration
- Social Security

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (requires Qdrant and Redis)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd ui

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## API Endpoints

### Query
```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "How to apply for citizenship?",
  "top_k": 5,
  "use_hybrid": true,
  "session_id": "optional_session_id"
}
```

### Upload Document
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

file: document.pdf
```

### Get Statistics
```bash
GET /api/v1/stats

Response:
{
  "total_documents": 134,
  "collection_name": "nepal_gov_docs",
  "status": "active"
}
```

### List Documents
```bash
GET /api/v1/documents

Response:
{
  "documents": [
    {
      "filename": "passport_application.pdf",
      "size_mb": 0.84,
      "uploaded_at": 1765095365.68
    }
  ]
}
```

### Health Check
```bash
GET /api/v1/health

Response:
{
  "status": "healthy",
  "service": "Nepal RAG Assistant"
}
```

## Project Structure

```
nepal-rag-assistant/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/               # API routes & dependencies
│   │   │   ├── main.py        # FastAPI app
│   │   │   ├── routes.py      # API endpoints
│   │   │   └── dependencies.py
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── logger.py      # Logging
│   │   ├── embedding/         # Embeddings
│   │   │   └── embeddings.py
│   │   ├── ingestion/         # Document processing
│   │   │   └── pdf_loader.py
│   │   ├── llm/               # LLM integration
│   │   │   └── llm.py         # Gemini wrapper
│   │   ├── retrieval/         # RAG retrieval
│   │   │   └── retriever.py
│   │   ├── vectorstore/       # Vector database
│   │   │   └── qdrant_client.py
│   │   ├── cache/             # Caching layer
│   │   │   ├── cache_manager.py
│   │   │   └── memory_manager.py
│   │   └── rag_pipeline.py    # Main RAG orchestrator
│   ├── Dockerfile
│   └── data/                  # Data storage
│       └── uploads/
├── ui/                        # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── ChatHeader.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessages.tsx
│   │   │   ├── QuickActions.tsx
│   │   │   └── ServiceSidebar.tsx
│   │   ├── services/          # API service layer
│   │   │   └── api.ts         # Backend API calls
│   │   └── App.tsx            # Main app
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml         # Docker orchestration
├── requirements.txt           # Python dependencies
└── README.md
```

## Configuration

Edit `backend/src/core/config.py` or set environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | LLM to use (gemini/openai) |
| `GEMINI_API_KEY` | - | Google Gemini API key |
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `1000` | Text chunk size |
| `CHUNK_OVERLAP` | `200` | Chunk overlap |
| `TOP_K` | `5` | Number of documents to retrieve |
| `QDRANT_URL` | - | Qdrant cloud URL |
| `QDRANT_API_KEY` | - | Qdrant API key |
| `REDIS_HOST` | `redis` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |

## Testing

```bash
# Test backend health
curl http://localhost:8000/api/v1/health

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How to apply for citizenship?", "top_k": 5, "use_hybrid": true}'

# Test document upload
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"

# Get statistics
curl http://localhost:8000/api/v1/stats

# List documents
curl http://localhost:8000/api/v1/documents
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **LLM**: Google Gemini 2.5-flash / OpenAI GPT-4
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: Qdrant (cloud-based)
- **Cache**: Redis 7
- **Document Processing**: PyPDF2, PyMuPDF
- **Language**: Python 3.10+

### Frontend
- **Framework**: React 18.3 with TypeScript
- **Build Tool**: Vite 6.3
- **UI Library**: Radix UI, Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Fetch API
- **Web Server**: Nginx (Alpine)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Services**: 4 containers (frontend, backend, redis, qdrant)
- **Networks**: Bridge network for inter-service communication

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Qdrant Connection Error
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart Qdrant
docker-compose restart qdrant

# Check Qdrant logs
docker logs nepal-rag-qdrant
```

### Redis Connection Error
```bash
# Check if Redis is running
docker ps | grep redis

# Restart Redis
docker-compose restart redis

# Test Redis connection
docker exec -it nepal-rag-redis redis-cli ping
```

### Frontend Not Loading
```bash
# Rebuild frontend
docker-compose build frontend

# Check nginx logs
docker logs nepal-rag-frontend

# Access frontend container
docker exec -it nepal-rag-frontend sh
```

### Backend API Errors
```bash
# Check backend logs
docker logs nepal-rag-backend

# Restart backend
docker-compose restart backend

# Check environment variables
docker exec -it nepal-rag-backend env | grep GEMINI
```

## License

MIT License - Feel free to use this project for educational and commercial purposes.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for React components
- Write unit tests for new features
- Update documentation for API changes
- Test Docker builds before submitting PR

## Contact & Support

- **GitHub**: [@supremkc05](https://github.com/supremkc05)
- **Project Repository**: [Nepal-Government-RAG-Assistant](https://github.com/supremkc05/Nepal-Government-RAG-Assistant)
- **Issues**: [Report bugs or request features](https://github.com/supremkc05/Nepal-Government-RAG-Assistant/issues)

## Acknowledgments

- Qdrant for vector database
- Google Gemini for LLM capabilities
- Sentence Transformers for embeddings
- FastAPI and React communities

