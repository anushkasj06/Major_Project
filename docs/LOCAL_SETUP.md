# Local Setup Guide

## Prerequisites

| Requirement | Version | How to install |
|------------|---------|----------------|
| Docker Desktop | 4.x+ | https://www.docker.com/products/docker-desktop |
| Docker Compose | v2+ | Included with Docker Desktop |
| Git | Any | https://git-scm.com |

**Windows users:** Enable WSL2 in Docker Desktop settings for best performance.

---

## Step-by-Step Setup

### 1. Get API Keys (Free)

**Gemini API** (primary LLM — free tier):
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key

**Groq API** (fallback LLM — free tier):
1. Go to https://console.groq.com/
2. Sign up / Sign in
3. API Keys → Create API Key
4. Copy the key

### 2. Clone and Configure

```bash
git clone <your-repo-url> arambh
cd arambh

# Create .env from template
cp .env.example .env
```

Edit `.env` and fill in:
```
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
JWT_SECRET_KEY=any_random_32+_char_string_here
MONGO_ROOT_PASSWORD=choose_a_password
```

### 3. Start All Services

```bash
docker compose up --build
```

**First run takes 5–15 minutes** because:
- Docker downloads ~2GB of model weights (HuggingFace)
- Python packages are installed

Subsequent starts take ~30 seconds.

### 4. Verify Everything is Running

```bash
docker compose ps
```

You should see all services as "running":
- arambh_mongodb
- arambh_redis
- arambh_qdrant
- arambh_backend
- arambh_ai
- arambh_crawler
- arambh_celery
- arambh_frontend

### 5. Access the App

| URL | Service |
|-----|---------|
| http://localhost:3000 | Frontend (main app) |
| http://localhost:8000/api/docs | Backend API docs |
| http://localhost:6333/dashboard | Qdrant vector DB UI |
| http://localhost | Nginx proxy |

Default login: `admin@arambh.local` / `admin123`

---

## Seeding College Data

### Option A: Upload PDFs via Admin Dashboard
1. Login → Admin Dashboard → Documents tab
2. Click "Upload PDF / DOCX"
3. Upload official college brochures, fee structures, placement reports

### Option B: Crawl a College Website
1. Admin Dashboard → Crawler tab
2. Enter college URL (e.g., `https://coep.org.in`)
3. Click "Start Crawl"
4. Wait for completion (~2–5 minutes per site)

### Option C: Use the API directly
```bash
curl -X POST http://localhost:8001/ai/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://coep.org.in/fees", "college_id": "coep_id", "college_name": "COEP"}'
```

---

## Running Tests

```bash
# Backend unit tests
docker compose exec backend pytest tests/ -v

# AI services tests
docker compose exec ai-services pytest tests/ -v

# Crawler tests
docker compose exec crawler pytest tests/ -v

# RAG evaluation
docker compose exec ai-services python -m app.utils.evaluation
```

---

## Troubleshooting

### "Cannot connect to MongoDB"
```bash
docker compose logs mongodb
# Wait for "MongoDB init process complete" in logs
docker compose restart backend ai-services
```

### "AI services OOMKilled" (Out of memory)
Increase Docker memory limit:
- Docker Desktop → Settings → Resources → Memory → Set to 6GB+

Or use a smaller embedding model in `.env`:
```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### "Qdrant collection not found"
```bash
docker compose restart ai-services
# The collection is created automatically on startup
```

### "Port already in use"
Change ports in `docker-compose.yml` or stop conflicting services:
```bash
# Find what's using port 3000
lsof -i :3000   # Mac/Linux
netstat -ano | findstr :3000  # Windows
```

### Frontend not loading
```bash
docker compose logs frontend
docker compose restart frontend
```

### Reset everything and start fresh
```bash
docker compose down -v   # -v removes all volumes (clears data)
docker compose up --build
```

---

## Common Operations

### Stop all services
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f backend     # Backend logs
docker compose logs -f ai-services # AI logs
docker compose logs -f crawler     # Crawler logs
```

### Rebuild a specific service after code change
```bash
docker compose up --build backend
docker compose up --build ai-services
```

### Connect to MongoDB shell
```bash
docker compose exec mongodb mongosh -u admin -p arambh_secret arambh
```

### Inspect Qdrant
Open: http://localhost:6333/dashboard
Click on "arambh_docs" collection to see indexed vectors.
