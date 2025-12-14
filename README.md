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

### 4. Access Application

- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Backend API: http://localhost:8000

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload

# Frontend
cd ui
npm install
npm run dev
```

## API Endpoints

- `POST /api/v1/query` - Query the RAG system
- `POST /api/v1/upload` - Upload documents
- `GET /api/v1/stats` - Get statistics
- `GET /api/v1/documents` - List documents
- `GET /api/v1/health` - Health check



## Tech Stack

- **Backend**: FastAPI, Python 3.10+, Google Gemini 2.5-flash
- **Frontend**: React 18.3, TypeScript, Vite, Tailwind CSS
- **Vector DB**: Qdrant
- **Cache**: Redis
- **Container**: Docker + Docker Compose

## License

MIT License

## Contributing

Contributions welcome! Fork, create a feature branch, and submit a PR.

## Contact

- GitHub: [@supremkc05](https://github.com/supremkc05)
- Issues: [Report bugs](https://github.com/supremkc05/Nepal-Government-RAG-Assistant/issues)
