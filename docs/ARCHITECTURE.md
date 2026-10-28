# Arambh — System Architecture

## Component Interaction Diagram

```
Browser (React SPA)
     │
     │ HTTP/SSE
     ▼
Nginx (Port 80)
     │
     ├──/api/*──► FastAPI Backend (Port 8000)
     │               │ JWT Auth
     │               │ Rate Limiting
     │               │ MongoDB (users, sessions, colleges, docs)
     │               │ Redis (cache, sessions)
     │               │
     │               │ HTTP forward
     │               ├──► AI Services (Port 8001)
     │               │         │
     │               │         ├── LangGraph Pipeline
     │               │         │    └── Query → Retrieve → Generate → Validate
     │               │         ├── Qdrant (vector search)
     │               │         ├── HuggingFace Embeddings (local)
     │               │         ├── Gemini API (primary LLM)
     │               │         └── Groq API (fallback LLM)
     │               │
     │               └──► Crawler Service (Port 8002)
     │                         │
     │                         ├── Celery Workers
     │                         ├── Async Spider (httpx + BS4)
     │                         └── PDF Downloader
     └──/*──────► React Frontend (Port 3000)
```

## Data Flow: User Query

1. User types query in React chat UI
2. POST /api/chat/message (JWT authenticated)
3. Backend forwards to AI Services
4. AI Services:
   a. Query Understanding Agent → detects intent + entities
   b. Hybrid Retrieval → Qdrant dense search + BM25
   c. Reciprocal Rank Fusion → combine results
   d. Cross-encoder Reranking → top-K most relevant
   e. Prompt Assembly → context + history + query
   f. LLM Generation → Gemini/Groq streaming
5. SSE stream back through Backend → Browser
6. Message saved to MongoDB (both user msg + assistant response)

## Data Flow: Admin Document Upload

1. Admin uploads PDF via /api/documents/upload
2. Backend saves file to /uploads volume
3. Backend creates document record in MongoDB (status: pending)
4. Backend POSTs to AI Services /ai/ingest
5. AI Services:
   a. Extract text (pdfplumber → pypdf fallback)
   b. Clean text
   c. Chunk (RecursiveCharacterTextSplitter)
   d. Embed (HuggingFace all-MiniLM-L6-v2)
   e. Upsert to Qdrant
6. MongoDB document status → "indexed"

## Data Flow: Web Crawl

1. Admin triggers crawl via /api/crawler/start
2. Backend creates crawler_job in MongoDB
3. Backend forwards to Crawler Service
4. Crawler Service dispatches Celery task
5. Celery Worker:
   a. Async spider crawls site (respects robots.txt, rate limits)
   b. Extracts text via trafilatura
   c. Downloads PDFs found on pages
   d. POSTs text to AI Services /ai/ingest/url
6. MongoDB crawler_job updated with progress

## Database Schemas

### MongoDB Collections

**users**: _id, name, email, hashed_password, role, preferred_language, created_at
**conversations**: _id, user_id, session_id, messages[], created_at, updated_at
**colleges**: _id, name, college_type, location, fees, placements, cutoffs, branches, ranking
**documents**: _id, filename, college_id, document_type, status, chunk_count, file_path
**crawler_jobs**: _id, url, college_id, status, pages_crawled, pages_indexed, created_at
**query_analytics**: _id, session_id, query, intent, confidence, was_helpful, created_at

### Qdrant Collection: arambh_docs

Vectors: 384-dimensional dense (all-MiniLM-L6-v2)
Payload fields:
  - text: str
  - college_id: str (keyword index)
  - college_name: str
  - doc_type: str (keyword index)
  - source_url: str
  - source_file: str
  - chunk_index: int
  - metadata: dict
