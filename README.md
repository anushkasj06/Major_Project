# 🎓 Arambh — Multi-Agent RAG Admission Chatbot

> Final Year Major Project — Scalable Multi-Agent RAG-Powered Admission Assistance Chatbot  
> with Real-Time College Data Retrieval

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NGINX (Port 80)                        │
└────────────┬───────────────────────────────┬────────────────┘
             │                               │
    ┌────────▼────────┐            ┌─────────▼────────┐
    │  React Frontend  │            │  FastAPI Backend  │
    │  (Port 3000)     │            │  (Port 8000)      │
    │  Vite + Tailwind │            │  JWT Auth + REST  │
    └─────────────────┘            └────────┬──────────┘
                                            │ HTTP
                              ┌─────────────▼──────────────┐
                              │      AI Services            │
                              │      (Port 8001)            │
                              │                             │
                              │  LangGraph RAG Pipeline     │
                              │  ┌─────────────────────┐   │
                              │  │ Query Understanding  │   │
                              │  │ ↓                   │   │
                              │  │ Hybrid Retrieval    │   │
                              │  │ ↓                   │   │
                              │  │ Reranking           │   │
                              │  │ ↓                   │   │
                              │  │ Response Generation │   │
                              │  │ ↓                   │   │
                              │  │ Validation          │   │
                              │  └─────────────────────┘   │
                              │                             │
                              │  Gemini API (Primary)       │
                              │  Groq/Llama (Fallback)      │
                              │  HuggingFace Embeddings     │
                              └──────────┬──────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────┐
              │                          │                   │
   ┌──────────▼──────┐       ┌───────────▼──────┐  ┌────────▼──────┐
   │    MongoDB       │       │     Qdrant        │  │    Redis      │
   │   (Port 27017)   │       │   (Port 6333)     │  │  (Port 6379)  │
   │  Users/Chats/    │       │  Vector Search    │  │  Cache/Queue  │
   │  Colleges/Docs   │       │  (384-dim dense)  │  │               │
   └─────────────────┘       └───────────────────┘  └───────────────┘
```

---

## 🚀 Quick Start (Local — 5 Steps)

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine + Compose (Linux)
- 8GB RAM recommended
- API Keys: [Gemini Free](https://makersuite.google.com/app/apikey) + [Groq Free](https://console.groq.com/)

### 1. Clone & Configure
```bash
git clone <repo>
cd arambh
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and GROQ_API_KEY
```

### 2. Start Everything
```bash
docker compose up --build
```
First run downloads ~2GB of model weights. Subsequent starts are fast.

### 3. Open the App
| Service | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:3000 |
| 📡 Backend API | http://localhost:8000/api/docs |
| 🔍 Qdrant UI | http://localhost:6333/dashboard |
| 🗄️ Mongo Express | `docker compose --profile monitoring up` → http://localhost:8081 |

### 4. Login
Default admin: `admin@arambh.local` / `admin123`

### 5. Add College Data
- Upload PDFs via Admin Dashboard → Documents
- Trigger web crawls via Admin Dashboard → Crawler
- Or use the API to bulk-import

---

## 📁 Project Structure

```
arambh/
├── frontend/              # React + Vite + Tailwind
│   ├── src/
│   │   ├── pages/         # ChatPage, AdminPage, Landing, Auth
│   │   ├── components/    # Reusable UI components
│   │   ├── store/         # Zustand state (auth, chat)
│   │   └── services/      # API client, streaming
│   └── Dockerfile
│
├── backend/               # FastAPI + JWT Auth
│   ├── app/
│   │   ├── api/routes/    # auth, chat, colleges, admin, crawler
│   │   ├── core/          # config, db, redis, security
│   │   ├── models/        # Pydantic schemas
│   │   └── repositories/  # MongoDB data access layer
│   └── Dockerfile
│
├── ai-services/           # RAG + LangGraph Agents
│   ├── app/
│   │   ├── agents/        # LangGraph nodes, LLM provider
│   │   ├── rag/           # vector_store, retriever, chunker, ingestion
│   │   ├── embeddings/    # HuggingFace sentence-transformers
│   │   ├── memory/        # Conversation memory
│   │   └── prompts/       # Prompt templates
│   └── Dockerfile
│
├── crawler/               # Async web spider + Celery
│   ├── app/
│   │   ├── spider.py      # Async crawler with robots.txt, rate limiting
│   │   ├── celery_app.py  # Task queue for background crawling
│   │   └── routes.py      # REST API for crawler control
│   └── Dockerfile
│
├── devops/
│   ├── docker/            # mongo-init.js
│   └── nginx/             # nginx.conf
│
├── docs/                  # API.md and architecture docs
├── docker-compose.yml     # Full local stack
└── .env.example           # Environment template
```

---

## 🤖 MCP Agent Pipeline (LangGraph)

```
User Query
    │
    ▼
[1] Query Understanding Agent
    • Intent detection (fees/placement/cutoff/scholarship/...)
    • Entity extraction (college name, branch, year, category)
    • Language detection (en/hi/mr)
    │
    ▼
[2] Hybrid Retrieval Agent
    • Dense vector search (Qdrant, sentence-transformers)
    • BM25 keyword search
    • Reciprocal Rank Fusion
    • Cross-encoder reranking
    │
    ▼
[3] Response Generation Agent
    • Gemini 1.5 Flash (primary, free tier)
    • Groq/Llama-3.1 (fallback, free tier)
    • Grounded in retrieved context only
    • Citation generation
    │
    ▼
[4] Validation Agent
    • Confidence scoring
    • Low-confidence disclaimer injection
    │
    ▼
Streaming SSE Response to Frontend
```

---

## 🔧 Environment Variables

See `.env.example` for full reference. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini (free tier) | Yes |
| `GROQ_API_KEY` | Groq API for Llama (free) | Yes |
| `JWT_SECRET_KEY` | Min 32 chars random string | Yes |
| `MONGO_ROOT_PASSWORD` | MongoDB root password | Yes |

---

## 🧪 Running Tests

```bash
# Backend tests
docker compose exec backend pytest tests/ -v

# AI services tests
docker compose exec ai-services pytest tests/ -v

# RAG evaluation
docker compose exec ai-services python -m app.utils.evaluation
```

---

## 📊 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Zustand |
| Backend | Python FastAPI, JWT, Motor (async MongoDB) |
| AI/RAG | LangChain, LangGraph, Gemini API, Groq/Llama |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (free, local) |
| Vector DB | Qdrant (local Docker) |
| Database | MongoDB 7.0 (local Docker) |
| Queue | Redis + Celery |
| Crawler | httpx, BeautifulSoup, Trafilatura, Playwright |
| DevOps | Docker Compose, Nginx |

---

## 🌐 Multilingual Support

- **English** (default)
- **Hindi** (हिन्दी) — Devanagari auto-detection
- **Marathi** (मराठी) — Marathi-specific word detection

Language is auto-detected from user input and the LLM responds in the same language.

---

## ☁️ Future AWS Migration

When ready to deploy to cloud:

1. Replace **MongoDB** → MongoDB Atlas or AWS DocumentDB
2. Replace **Qdrant** container → Qdrant Cloud or AWS OpenSearch
3. Replace **Redis** → AWS ElastiCache
4. Replace **local file storage** → AWS S3 (update `UPLOAD_DIR`)
5. Deploy services as **ECS Fargate** tasks or **EC2** with Docker Compose
6. Add **CloudFront** in front of the frontend
7. Use **AWS Secrets Manager** for API keys

All environment variables are already externalized — migration is just a config change.

---

## 📝 License

MIT — Free for academic and personal use.

Built with ❤️ as a Final Year Major Project.
#   M a j o r _ P r o j e c t  
 